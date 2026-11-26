# Tasks

## 1. Filtro no core

- [x] 1.1 Criar `src/journal/app/filter.py` com `KeywordFilter` (normalização sem acento/caixa, palavra inteira, exclude vence) e exportar em `journal.app`; testes em `tests/test_filter.py` cobrindo os cenários de filtro da spec
- [x] 1.2 `BuildJournal` aceita `article_filter` e `max_articles` opcionais e aplica deduplicar → filtrar → ordenar → limitar; `BuildReport.fetched`; testes em `tests/test_build.py` (filtro vazio publica lista vazia, limite fica com os mais recentes)

## 2. Configuração e CLI

- [x] 2.1 `load_config` lê e valida `[filter]` (tabela, listas de strings não vazias, inteiro positivo, chaves desconhecidas) e expõe em `Config`; testes em `tests/test_config.py`
- [x] 2.2 CLI passa filtro e limite ao build e imprime "published N of M articles"; testes em `tests/test_cli.py`

## 3. Documentação e verificação

- [x] 3.1 README: seção `[filter]` com exemplo; comentário de exemplo no `journal.toml` (sem ativar o filtro)
- [x] 3.2 `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam; `uv run journal build` com um filtro de teste numa cópia da config publica poucos artigos
