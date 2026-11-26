# Tasks

## 1. Domínio e fonte

- [x] 1.1 `Article.image_caption` e `Article.image_credit` opcionais; teste em `tests/test_article.py`
- [x] 1.2 RSS lê `media_text` (texto puro) e o primeiro `media_credit`, só quando há imagem; casos na fixture `images.xml` e teste em `tests/test_rss_source.py`

## 2. Site

- [x] 2.1 Figura com `<figcaption>` na página da notícia (descrição + linha de crédito), campos novos no `articles.json`, CSS da legenda; testes em `tests/test_static_site.py` (com crédito, sem crédito, escape)

## 3. Verificação

- [x] 3.1 `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam; captura de tela de uma notícia da Ars Technica (com crédito) e de uma da BBC (sem crédito)
