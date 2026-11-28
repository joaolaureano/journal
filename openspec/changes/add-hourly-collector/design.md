# Design

## Context

- Cada fonte implementa `SourcePort.fetch() -> list[Article]`. `config.py` envolve uma fonte em `Sectioned` (de `app/`) quando ela declara `section` ou `kind`. `Sectioned.fetch()` carimba esses campos em cada item.
- CNN Brasil e Jovem Pan só têm feed geral, com esportes e variedades. A seção vem no endereço do link (`/politica/`, `/economia/`, `/internacional/`); as categorias do feed não servem, porque as de economia da CNN variam.
- O site e o cache da IA usam o mesmo `StoragePort` (`exists`/`read`/`write`). Ele é `LocalStorage` em `dist/` ou `S3Storage` no bucket. Na Lambda, `handler` troca o publisher do config por um `StaticSitePublisher(S3Storage(...))` depois de carregar a configuração. Por isso o storage certo só é conhecido em `cli.run`, que já o pega com `getattr(publisher, "storage", None)` para o cache da DeepSeek.
- `LocalStorage` só escreve em diretório vazio ou que já tenha um marcador de site (`SITE_MARKERS`).
- A Lambda tem 256 MB e 600 s. A agenda diária usa o EventBridge Scheduler.

## Goals / Non-Goals

**Goals:**
- A edição das 08:00 vê tudo o que cada feed mostrou nas últimas `hours` horas.
- Coleta e edição passam pelo mesmo caminho de leitura. A edição também atualiza o pool.
- Tudo testável localmente com storage em memória e fontes falsas, sem rede e sem DeepSeek.

**Non-Goals:**
- Mudar a seleção da edição. `max_per_section`, `max_articles`, o histórico e o filtro continuam iguais e agora só recebem mais candidatos.
- Escolher quais fontes passam pelo pool. Todas passam quando `[pool]` existe.

## Decisions

1. **O pool é um adapter que envolve a fonte (`adapters/pool.py`, classe `Pooled`).** `Pooled(source, storage, hours, now)` implementa `SourcePort`. `fetch()` lê o feed, lê a entrada do pool, junta as duas por `Article.key` com o feed ganhando, corta pela janela e pelo limite de 1000 itens, salva e devolve. Não há porta nova no core: o build continua vendo só fontes.
   - *Alternativa:* uma `PoolPort` no core, com o build juntando feed e pool. Isso mexeria em `BuildJournal` e no seu spec sem ganho. O `Pooled` dá o mesmo resultado sem tocar no core.

2. **O `Pooled` envolve a fonte de dentro do `Sectioned`.** Em `cli.py`, uma função `pooled(sources, storage, hours)` troca `Sectioned(s)` por `Sectioned(Pooled(s.source, ...), s.section, s.kind, s.paths)` e as outras fontes por `Pooled(s, ...)`. O pool guarda os itens crus, e `section` e `kind` vêm sempre do `journal.toml` atual: mudar a seção de uma fonte vale na hora também para o que já está guardado.
   - *Alternativa:* envolver por fora. Seria uma linha a menos, mas os itens guardados ficariam com a seção antiga por até 48 h.

3. **Um arquivo por fonte: `pool/<sha256(nome)[:16]>.json`**, com `{"source": nome, "articles": [...]}`. O hash evita colisão e caracteres estranhos de nomes como "arXiv (cs.DS, cs.IT)". O nome dentro do arquivo serve para ler à mão. A leitura descarta um arquivo cujo `source` não bate com o nome da fonte.
   - *Alternativa:* um arquivo por dia. Exigiria ler vários dias a cada fetch e limpar os antigos. Com um arquivo por fonte, a limpeza é o corte pela janela a cada escrita, e não precisa de regra de expiração para os objetos atuais.

4. **Serialização no próprio adapter:** os campos de `Article` (menos `id`, que é derivado), com `published_at` em ISO 8601. Cada item lido volta por `Article(**campos)`, que valida. Um item recusado é descartado sozinho, e um arquivo inválido conta como vazio (spec "Pool failures stay with their source").

5. **Falha do feed propaga, e o pool fica intacto.** A fonte falha como hoje e não escreve nada. Na edição, isso significa que os itens guardados daquela fonte ficam de fora naquele dia, mesmo existindo.
   - *Alternativa:* devolver o pool quando o feed falha. A edição ganharia os itens, mas `SourcePort` não tem como devolver itens e erro ao mesmo tempo, e a falha sumiria do relatório. Fica como atalho com comentário no código (`shortcut: ...`). A melhoria vem quando o relatório aceitar um aviso por fonte.

6. **`journal collect` e o handler reusam `cli.run`.** Uma função `collect(config) -> CollectReport` monta as mesmas fontes com pool e chama `fetch()` em cada uma, sequencialmente, como o build. Ela não monta summarizer nem publica. No handler, `event.get("action") == "collect"` desvia para ela antes de `_load_deepseek_key`, então a coleta nunca lê a chave.

7. **O filtro por endereço fica no `Sectioned`.** `paths` é aceito em qualquer fonte, como `section` e `kind`, e `Sectioned.fetch()` descarta os itens cujo caminho do link não começa por um dos prefixos, antes de carimbar seção e tipo. A ordem fica feed cru → pool → filtro → seção, então o pool guarda o feed inteiro e mudar `paths` vale na hora também para o que já está guardado.
   - *Alternativa:* filtrar antes do pool, numa camada própria. O pool ficaria menor, mas seria mais um wrapper para montar em `cli.pooled`.
   - *Atalho:* as três entradas da CNN leem o mesmo feed três vezes por execução e guardam três cópias iguais no pool, ~1 MB cada. `shortcut: um pool por URL de feed resolveria; vale quando houver muitos feeds repetidos`.

8. **`pool` entra em `SITE_MARKERS`.** Sem isso, um `dist/` que só recebeu coletas, sem nenhuma edição ainda, seria recusado na escrita seguinte.

9. **Infra:** um `aws_scheduler_schedule.collect` com `cron(30 * * * ? *)`, variável `collect_schedule_expression` e `input = jsonencode({action = "collect"})`. Ele reusa o papel do scheduler, que já pode invocar a função. Também entra uma segunda regra de ciclo de vida, com filtro `prefix = "pool/"` e `noncurrent_days = 1`. Com regras sobrepostas, o S3 aplica a expiração mais curta. Sem essa regra, as 24 versões diárias de cada arquivo ficariam 30 dias.

## Risks / Trade-offs

- [Um feed muito ativo enche o arquivo] → limite fixo de 1000 itens por fonte, os mais novos. Com texto completo, ~3 KB por item, são ~3 MB no pior caso, dentro dos 256 MB da Lambda.
- [Coleta e edição escrevem o mesmo arquivo ao mesmo tempo] → a edição roda às :00 e a coleta às :30, e cada coleta leva segundos. No pior caso, a última escrita vence e só a coleta seguinte recupera o que faltou, sem corromper nada: cada `write` é atômico no S3 e no `LocalStorage`.
- [O pool fica legível pelo CloudFront, como o `llm-cache/`] → é texto de feed, já público, e os nomes de arquivo são hashes. Aceito.
- [A edição recebe muito mais candidatos, por exemplo ~35 do g1 em vez de ~10] → `max_per_section` continua cortando a seção. O agrupamento por história, no próximo passo, é quem vai usar o volume.
- [A CNN e a Jovem Pan mudarem o padrão dos endereços] → a seção some sem erro. Uma seção vazia numa edição é o sinal; a checagem é rever os `paths`.
- [A JOTA mistura opinião e eventos patrocinados] → entram como notícia por enquanto. Quem separa é a classificação por tema e por história do passo 3.

## Migration Plan

1. Mesclar com `[pool]` e as cinco entradas da CNN e da Jovem Pan no `journal.toml`. A edição seguinte já cria o pool, e as anteriores não mudam.
2. Rodar `tofu apply` com o perfil `agent`: cria a agenda de coleta e a regra de ciclo de vida. O CI atualiza só o código da Lambda.
3. Rollback: remover `[pool]` do `journal.toml` faz as fontes voltarem a ler só o feed. Os arquivos em `pool/` podem ficar ou ser apagados.
