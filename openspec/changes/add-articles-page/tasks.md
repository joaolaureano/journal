# Tasks

## 1. Domain and configuration

- [x] 1.1 `Article.kind` (`noticia` default, `artigo`), validated, with tests
- [x] 1.2 `Sectioned` stamps an optional section and kind; `config._source` accepts `kind` on any source and rejects other values; config tests
- [x] 1.3 Per-section cap keyed by section and kind, with the "news do not push articles out" test

## 2. Static site

- [x] 2.1 `_edition_page` renders one kind; publish writes `artigos.html` in the edition and at the root (before the root `index.html`)
- [x] 2.2 Tabs below the masthead with `aria-current`, and their styles
- [x] 2.3 Reading time on article items with a body
- [x] 2.4 Back link by kind on article pages; `kind` in `articles.json`
- [x] 2.5 `artigos.html` on the short cache in `S3Storage`
- [x] 2.6 Tests for the static-site and aws-deploy delta scenarios

## 3. Ship

- [x] 3.1 `kind = "artigo"` in `journal.toml` on the blogs, The Conversation Brasil, Pesquisa FAPESP, IEEE Spectrum, Krebs and Agência Pública
- [x] 3.2 Ruff, the whole suite, `openspec validate --strict`; local edition and screenshots of both pages
- [x] 3.3 README, commit, push, CI deploy, publish an edition, archive the change
