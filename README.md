# journal

Portal estático de notícias/ciência gerado automaticamente a partir de fontes configuráveis.

## Arquitetura (ports and adapters)

```
src/journal/
  domain/    entidades puras, sem dependências externas
  ports/     interfaces que o core espera (fontes, publicação)
  adapters/  implementações concretas das ports (RSS, site estático, ...)
  app/       casos de uso que orquestram ports
```

O core (`domain`, `ports`, `app`) não conhece nenhum adapter específico.

## Uso

```sh
uv run journal build                       # lê ./journal.toml
uv run journal build --config outro.toml
```

Busca as fontes configuradas, remove duplicatas, ordena do mais recente ao mais antigo e grava a
**edição do dia** em `dist/`:

```
dist/
  index.html                      edição mais recente
  edicoes/index.html              arquivo: todas as edições, da mais nova à mais antiga
  edicoes/2026-11-26/             uma pasta por edição
    index.html                    lista de notícias da edição
    articles/<id>.html            uma página por artigo
    articles.json                 os mesmos dados em JSON
  edicoes/2026-11-26-2/           2ª execução no mesmo dia (revisão 2)
  editions.json                   manifesto: data, revisão, pasta e nº de artigos
  seen.json                       histórico: notícia -> dia em que saiu pela 1ª vez
  style.css
```

Abra `dist/index.html` direto no navegador ou sirva a pasta em qualquer hospedagem estática.

- A data da edição e os horários exibidos seguem o `timezone` da config (padrão
  `America/Sao_Paulo`).
- Com `section` nas fontes, a edição sai em blocos por seção, na ordem da config; fontes sem seção
  vão para "Outras".
  Abaixo da data da edição, um índice leva direto a cada seção.
- Notícias e artigos: com `kind = "artigo"` numa fonte (qualquer tipo, como `section`), seus itens
  vão para `artigos.html`, a página de artigos da edição; o resto fica em `index.html`. Abas
  "Notícias" e "Artigos" abaixo do nome do jornal alternam entre as duas, e artigos com texto
  completo mostram o tempo de leitura. O limite por seção conta notícias e artigos à parte.
- Resumos: sem o rodapé "O post … apareceu primeiro em …" do WordPress e com no máximo ~400
  caracteres. Sem imagem nos campos de mídia, vale a primeira do texto completo do feed.
  Estatísticas do hnrss.org ("Article URL: …", "Points: …") não contam como resumo.
- Texto completo (`full_text = true` na fonte): a página da notícia mostra o texto mais longo que
  o feed manda (`content:encoded` ou a descrição), com parágrafos, listas, citações, links e as
  fotos no lugar. O HTML é remontado por uma lista de tags permitidas: scripts, iframes, vídeos,
  formulários, estilos, eventos, links `javascript:` e pixels de rastreamento ficam de fora, e a
  foto de capa não se repete. A lista da edição continua com o resumo.
- Toda página pede para não ser indexada (`<meta name="robots" content="noindex, nofollow">`).
- Toda página tem um menu fixo à esquerda com as 30 edições mais recentes (DD/MM/AAAA), a última
  edição e o arquivo. Aberto em telas largas, fechado no celular; o botão ☰ abre e fecha, só com
  CSS. Edições antigas mantêm o menu de quando foram geradas.
- Edições nunca são sobrescritas: rodar de novo no mesmo dia cria uma revisão nova.
- Uma notícia que saiu numa edição de um dia anterior não volta nas seguintes (`seen.json`, mesma
  normalização de URL da deduplicação, guardado por 90 dias). Uma revisão do mesmo dia refaz o dia
  inteiro, então pode repetir o que a revisão anterior trouxe.
- A edição é gravada primeiro; `editions.json` e `index.html` por último. Se falhar no meio, o
  site continua apontando para a edição anterior.
- Uma fonte que falha de forma passageira (rede, tempo esgotado, HTTP 5xx/408/429, resposta cortada
  ou feed quebrado) é tentada mais duas vezes, após 1 s e 2 s; um 403 ou 404 desiste na hora. Fonte
  que continua falhando fica de fora da edição e aparece no log.
- Se nenhuma fonte responder, o comando sai com código 1 e não toca em `dist/`.
- Por segurança, o build se recusa a escrever num diretório que já tenha outros arquivos e não seja
  um site do journal.

## Configuração

Para ter o seu próprio jornal, faça um fork e troque as fontes do `journal.toml`.

`journal.toml` declara as fontes (na ordem em que são lidas) e o publisher:

```toml
[[sources]]
type = "rss"
name = "Nature"                             # aparece nos artigos
url = "https://www.nature.com/nature.rss"
timeout = 10                                # opcional, segundos (> 0)
full_text = false                           # opcional: mostra o texto completo do feed
section = "Ciência"                         # opcional, vale para qualquer tipo de fonte
kind = "noticia"                            # opcional: "noticia" (padrão) ou "artigo"
paths = ["/politica/"]                      # opcional: só links cujo caminho começa assim

[publisher]
type = "static-site"
storage = { type = "local", out = "dist" }  # opcional; `out` relativo ao arquivo de config
```

`timezone` (chave de topo, antes de qualquer `[[sources]]`) define a data das edições.
`out = "dist"` direto em `[publisher]` é um atalho para o armazenamento local.

Para adicionar outra fonte RSS, basta outro bloco `[[sources]]`. Nenhum código muda.

`paths` serve para feeds gerais que separam as seções no endereço: com
`paths = ["/politica/"]`, só ficam os itens de `…/politica/…`, seja qual for o site. O mesmo feed
pode entrar em mais de uma seção, cada uma com seu `name` e seus `paths`.

Tipos embutidos: fonte `rss`, publisher `static-site`, armazenamento `local` e `s3`. Outros tipos vêm de
plugins.

### Filtro (opcional)

Sem a seção `[filter]`, tudo o que as fontes trazem é publicado. Com ela:

```toml
[filter]
include = ["selic", "juros", "ibovespa", "banco central"]  # pelo menos um termo
exclude = ["futebol"]                                       # nenhum destes
exclude_domains = ["folha.uol.com.br"]                      # nem links destes sites
max_articles = 5                                            # só os N mais recentes
max_age_days = 2                                            # só dos últimos N dias
max_per_section = 10                                        # no máximo N por seção
```

Os termos são procurados no título e no resumo, sem diferenciar maiúsculas nem acentos, como
palavras ou frases inteiras ("juros" não casa com "conjuros"). `exclude` vence `include`.
`exclude_domains` corta itens pelo endereço do link, contando os subdomínios
(`folha.uol.com.br` corta `www1.folha.uol.com.br`, mas `folha.com.br` não corta `minhafolha.com.br`):
serve para sites com paywall que aparecem dentro de outro feed. Todas as chaves são opcionais. Com ou sem filtro, artigos datados mais de um dia no futuro são
descartados (data errada no feed). O comando mostra quantos artigos passaram: `published 5 of 996 articles`.

### Coletor de hora em hora (opcional)

Um feed só lista os últimos itens: alguns cobrem só 1,5 h. Com a seção `[pool]`, cada leitura de
uma fonte guarda o que o feed mostrou e devolve também o que ele mostrou nas últimas `hours` horas.
O resultado fica no mesmo armazenamento do site, em `pool/`, um arquivo por fonte.

```toml
[pool]
hours = 48  # opcional (padrão 48): cobre de sábado a segunda, já que domingo não tem edição
```

`journal collect --config journal.toml` só lê as fontes e atualiza o pool: não publica nada e não
chama o modelo de IA. Rodado de hora em hora (na AWS, pela agenda `collect`), ele deixa a edição
do dia seguinte ver tudo o que cada feed mostrou. `journal build` também atualiza o pool. Sem
`[pool]`, as fontes são lidas só do feed, como antes.

### Aquecimento por IA (opcional)

Com a seção `[summarizer]` e a variável `DEEPSEEK_API_KEY`, cada item de `kind = "artigo"` ganha
um parágrafo curto escrito pelo DeepSeek (`deepseek-flash`, sem raciocínio) a partir do texto do
próprio feed. Ele aparece no lugar do resumo em `artigos.html` e acima do texto na página do
artigo, sempre marcado como IA. Notícias não passam pelo modelo.

```toml
[summarizer]
model = "deepseek-flash"
max_calls = 50           # chamadas pagas por edição
max_input_chars = 16000  # texto enviado por artigo, no máximo
timeout = 180            # segundos para a etapa inteira
```

O texto vai para a API só com a biblioteca padrão (`urllib`). As respostas ficam em cache em
`llm-cache/warmup/` no próprio armazenamento do site, então uma revisão no mesmo dia não paga de
novo. Sem chave, com o orçamento estourado, com erro ou timeout, o artigo sai como antes e o
motivo vai para o log (`warm-up failed: ...`).

## Escrevendo um plugin

Um plugin é um pacote Python instalado no mesmo ambiente que oferece tipos novos de fonte ou
publisher, sem alterar este repositório.

1. Implemente o adapter: uma fonte tem `fetch() -> list[Article]` e levanta `SourceError` em
   falha; um publisher tem `publish(articles)` e levanta `PublishError`.
2. Exponha um `AdapterType` com as opções aceitas:

   ```python
   from journal.config import AdapterType

   REDDIT = AdapterType(
       build=lambda options, config_dir: RedditSource(options["subreddit"]),
       required={"subreddit": str},
       optional={"limit": int},
   )
   ```

3. Declare o entry point no `pyproject.toml` do plugin; o nome é o `type` usado na config:

   ```toml
   [project.entry-points."journal.sources"]      # ou "journal.publishers", "journal.storages"
   reddit = "meu_pacote.reddit:REDDIT"
   ```

O journal valida as opções antes de chamar `build`, só importa o plugin quando a config usa o
tipo, e recusa um `type` oferecido por mais de um pacote.

API pública para plugins: `journal.config.AdapterType`, `journal.domain` (`Article`, `Edition`),
`journal.ports` (`SourcePort`, `PublisherPort`, `SourceError`, `PublishError`) e
`journal.adapters.storage.StoragePort` (`exists`, `read`, `write`) para novos armazenamentos.

## AWS

Edição de segunda a sábado às 8h numa Lambda, site no S3 + CloudFront: veja [deploy/README.md](deploy/README.md).
Com o CI ligado, um push na `main` publica o código e o `journal.toml` na Lambda.
Armazenamento no S3 também pela config: `storage = { type = "s3", bucket = "...", prefix = "" }`
(requer `journal[aws]`).

## Desenvolvimento

Requer [uv](https://docs.astral.sh/uv/).

```sh
uv sync                     # cria .venv e instala dependências
uv run pytest               # testes
uv run ruff check .         # lint
uv run ruff format --check .
```

O GitHub Actions (`.github/workflows/ci.yml`) roda o lint e os testes em todo push e pull request.

## Uso responsável

O journal só exibe o que cada feed distribui: título, resumo, imagem (quando o feed traz uma),
nome da fonte e um link para o original, e o texto completo só nas fontes com `full_text`. Ele não baixa a página do artigo, PDFs nem imagens: a
imagem é carregada direto do site de origem por quem abre a página, então o site publicado faz
requisições a esses domínios.

Quem usa o journal é responsável por:

- respeitar os termos de uso de cada fonte (muitos feeds permitem só uso pessoal e não comercial);
- respeitar a licença de cada artigo (ex.: Creative Commons BY exige crédito, BY-NC proíbe uso
  comercial) e não republicar texto completo de conteúdo protegido: `full_text` vem desligado;
  num site aberto, ligue só em fontes cuja licença permite (ex.: Agência Brasil, CC BY). O
  `journal.toml` deste repositório liga em mais fontes, para leitura pessoal;
- manter o crédito e o link para a fonte original ao publicar o site;
- identificar como tal qualquer resumo gerado por IA e não atribuir à fonte o que ela não disse.

Com `[summarizer]`, o texto dos artigos é enviado à API da DeepSeek. O parágrafo gerado vem
marcado como "Resumo gerado por IA a partir de <fonte>", ao lado do link para o original. O
conteúdo do feed é passado ao modelo como dado, nunca como instrução, e a resposta entra na página
como texto escapado, nunca como HTML.

Este projeto não é afiliado a nenhuma das fontes citadas na configuração.

## Licença

[MIT](LICENSE).
