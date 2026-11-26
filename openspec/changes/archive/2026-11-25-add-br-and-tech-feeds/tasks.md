# Tasks

## 1. Fontes

- [x] 1.1 Conferir que cada URL nova responde e é RSS/Atom (`RssSource(...).fetch()` sem erro e com artigos)
- [x] 1.2 Adicionar as fontes ao `journal.toml`, agrupadas por tema; verificar com `uv run journal build`

## 2. Teste

- [x] 2.1 Trocar `tests/test_journal_toml.py` para validar carga, ao menos uma fonte e nomes únicos; `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` passam
