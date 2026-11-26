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

Busca as fontes configuradas, remove duplicatas, ordena do mais recente ao mais antigo e grava o site em `dist/`:

```
dist/
  index.html            lista de notícias
  articles/<id>.html    uma página por artigo
  style.css
  articles.json         os mesmos dados em JSON
```

Abra `dist/index.html` direto no navegador ou sirva a pasta em qualquer hospedagem estática.

- Cada build substitui o site inteiro; se falhar no meio, o site anterior fica intacto.
- Se nenhuma fonte responder, o comando sai com código 1 e não toca em `dist/`.
- Por segurança, o build se recusa a escrever num diretório que já tenha outros arquivos e não seja um site do journal.

## Configuração

Para ter o seu próprio jornal, faça um fork e troque as fontes do `journal.toml`.

`journal.toml` declara as fontes (na ordem em que são lidas) e o publisher:

```toml
[[sources]]
type = "rss"
name = "Nature"                             # aparece nos artigos
url = "https://www.nature.com/nature.rss"
timeout = 10                                # opcional, segundos

[publisher]
type = "static-site"
out = "dist"                                # opcional, relativo ao arquivo de config
```

Para adicionar outra fonte RSS, basta outro bloco `[[sources]]`. Nenhum código muda.

Tipos embutidos: fonte `rss`, publisher `static-site`. Outros tipos vêm de plugins.

### Filtro (opcional)

Sem a seção `[filter]`, tudo o que as fontes trazem é publicado. Com ela:

```toml
[filter]
include = ["selic", "juros", "ibovespa", "banco central"]  # pelo menos um termo
exclude = ["futebol"]                                       # nenhum destes
max_articles = 5                                            # só os N mais recentes
max_age_days = 2                                            # só dos últimos N dias
```

Os termos são procurados no título e no resumo, sem diferenciar maiúsculas nem acentos, como
palavras ou frases inteiras ("juros" não casa com "conjuros"). `exclude` vence `include`. Todas as
chaves são opcionais. Com ou sem filtro, artigos datados mais de um dia no futuro são
descartados (data errada no feed). O comando mostra quantos artigos passaram: `published 5 of 996 articles`.

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
   [project.entry-points."journal.sources"]      # ou "journal.publishers"
   reddit = "meu_pacote.reddit:REDDIT"
   ```

O journal valida as opções antes de chamar `build`, só importa o plugin quando a config usa o
tipo, e recusa um `type` oferecido por mais de um pacote.

API pública para plugins: `journal.config.AdapterType`, `journal.domain.Article`,
`journal.ports` (`SourcePort`, `PublisherPort`, `SourceError`, `PublishError`).

## Desenvolvimento

Requer [uv](https://docs.astral.sh/uv/).

```sh
uv sync                     # cria .venv e instala dependências
uv run pytest               # testes
uv run ruff check .         # lint
uv run ruff format --check .
```

## Uso responsável

O journal só exibe o que cada feed distribui: título, resumo, imagem (quando o feed traz uma),
nome da fonte e um link para o original. Ele não baixa a página do artigo, PDFs nem imagens: a
imagem é carregada direto do site de origem por quem abre a página, então o site publicado faz
requisições a esses domínios.

Quem usa o journal é responsável por:

- respeitar os termos de uso de cada fonte (muitos feeds permitem só uso pessoal e não comercial);
- respeitar a licença de cada artigo (ex.: Creative Commons BY exige crédito, BY-NC proíbe uso
  comercial) e não republicar texto completo de conteúdo protegido;
- manter o crédito e o link para a fonte original ao publicar o site;
- identificar como tal qualquer resumo gerado por IA e não atribuir à fonte o que ela não disse.

Este projeto não é afiliado a nenhuma das fontes citadas na configuração.

## Licença

[MIT](LICENSE).
