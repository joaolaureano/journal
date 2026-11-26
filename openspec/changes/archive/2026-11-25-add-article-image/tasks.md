# Tasks

## 1. Domínio

- [x] 1.1 `Article.image: str | None = None`, validado como URL http(s); testes em `tests/test_article.py`

## 2. Fonte RSS

- [x] 2.1 Extrair a imagem de `media_content`, `media_thumbnail` e `enclosures` de imagem, descartando URLs inválidas; fixture com os casos da spec e testes em `tests/test_rss_source.py`

## 3. Site

- [x] 3.1 `image` no `articles.json`; `<img>` na lista e na página do artigo; CSS da miniatura e da imagem; testes em `tests/test_static_site.py`
- [x] 3.2 README: imagens em "Uso responsável" e no formato do `articles.json`

## 4. Verificação

- [x] 4.1 `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam; `uv run journal build` com os feeds reais gera artigos com imagem e as páginas mostram as fotos (captura de tela)
