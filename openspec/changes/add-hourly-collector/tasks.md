# Tasks

Tudo local, com fakes e storage em memória ou `tmp_path`. Nenhum teste e nenhum build local chama a DeepSeek: builds locais rodam com `env -u DEEPSEEK_API_KEY`.

## 1. Pool de uma fonte

- [ ] 1.1 Criar `adapters/pool.py` com `Pooled(source, storage, hours, now)`: lê o feed, lê `pool/<sha256(nome)[:16]>.json`, junta por `Article.key` com o feed ganhando, corta pela janela e pelos 1000 mais novos, salva e devolve
- [ ] 1.2 Serializar `Article` sem `id`, com `published_at` em ISO 8601. Na leitura, descartar o item recusado por `Article(**campos)` e tratar como vazio o arquivo inválido ou com `source` diferente
- [ ] 1.3 Propagar a falha do feed sem escrever o pool, com o comentário `shortcut:` da decisão 5. Transformar a falha de escrita do storage em `SourceError` com o nome da fonte
- [ ] 1.4 Adicionar `pool` a `SITE_MARKERS` em `adapters/storage.py`
- [ ] 1.5 Testes em `tests/test_pool.py`, um por cenário do spec `source-pool`: item que saiu do feed, item fora da janela, mesmo item no feed e no pool, entrada corrompida, feed fora do ar, limite de 1000. Mais um teste de `LocalStorage` aceitando um diretório que só tem `pool/`

## 2. Filtro por endereço

- [ ] 2.1 Em `config.py`, aceitar `paths` em qualquer fonte, como `section` e `kind`: lista não vazia de strings que começam com `/`, recusando outros valores com erro que cita `paths`
- [ ] 2.2 Em `app/sectioned.py`, dar a `Sectioned` o parâmetro `paths` e descartar os itens cujo caminho do link não começa por um dos prefixos, antes de carimbar seção e tipo
- [ ] 2.3 Testes em `tests/test_config.py` e `tests/test_build.py` (ou no teste do `Sectioned`) para os dois cenários do requisito "Optional path filter on every source"
- [ ] 2.4 Documentar `paths` no README

## 3. Configuração do pool

- [ ] 3.1 Em `config.py`, ler a tabela opcional `[pool]` com `hours` (inteiro positivo, padrão 48) para `Config.pool`, recusando chave desconhecida e valor inválido com o nome da chave
- [ ] 3.2 Testes em `tests/test_config.py`: tabela válida, `hours = 0`, chave `hour`, ausência da tabela
- [ ] 3.3 Documentar `[pool]` e `journal collect` no README

## 4. Coleta e build com pool

- [ ] 4.1 Em `cli.py`, criar `pooled(sources, storage, hours)`, que envolve a fonte de dentro do `Sectioned` (decisão 2) e preserva `paths`, e usá-la em `run` quando `config.pool` existe
- [ ] 4.2 Criar `collect(config)` e o subcomando `journal collect --config`, que imprime as falhas e o total guardado, sem summarizer e sem publicar. Sair com status 1 sem `[pool]`, com config inválida ou quando nenhuma fonte responde
- [ ] 4.3 Testes em `tests/test_cli.py`: a coleta grava o pool e não grava páginas nem `editions.json`; o build seguinte recebe o item que saiu do feed com a seção do `journal.toml` atual; erro sem `[pool]`

## 5. Lambda e infraestrutura

- [ ] 5.1 Em `aws_lambda.py`, desviar `{"action": "collect"}` para `collect` antes de `_load_deepseek_key` e devolver o total e as falhas
- [ ] 5.2 Testes em `tests/test_aws_lambda.py`: a coleta grava o pool no storage dado e não lê o SSM (fake que falha se chamado); um evento sem `action` continua gerando a edição
- [ ] 5.3 Em `deploy/`, criar a variável `collect_schedule_expression` (padrão `cron(30 * * * ? *)`), o `aws_scheduler_schedule.collect` com `input = jsonencode({action = "collect"})` e a regra de ciclo de vida para `pool/` com `noncurrent_days = 1`
- [ ] 5.4 Rodar `tofu fmt -check` e `tofu validate` em `deploy/`

## 6. Fontes

- [ ] 6.1 Em `journal.toml`, adicionar `[pool]` e as entradas CNN Brasil política (`/politica/`), CNN Brasil economia (`/economia/`), CNN Brasil internacional (`/internacional/`, seção Mundo), Jovem Pan política e Jovem Pan economia, com `full_text = true` e nomes únicos; tirar os comentários "entram com o filtro por endereço"
- [ ] 6.2 Conferir que `tests/test_journal_toml.py` passa, com nomes únicos e config válida
- [ ] 6.3 Rodar duas coletas locais e um build local com `env -u DEEPSEEK_API_KEY` sobre um diretório temporário, e conferir que `pool/` tem uma entrada por fonte, que a edição sai e que as seções da CNN e da Jovem Pan só têm itens do caminho certo

## 7. Verificação

- [ ] 7.1 Rodar `ruff check`, a suíte de testes completa e `openspec validate add-hourly-collector --strict`

## Workflow follow-up

- `tofu apply` com o perfil `agent` depois do merge, só com o OK do dono
- Arquivar a mudança depois que a coleta rodar na AWS
