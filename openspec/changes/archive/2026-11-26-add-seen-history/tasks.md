# Tasks

## 1. Core

- [x] 1.1 `dedup_key` no domínio e `Article.key`
- [x] 1.2 `HistoryPort` e descarte no `BuildJournal`, com `already_published` no relatório; testes (inclui variantes de URL)

## 2. Site estático

- [x] 2.1 `published_before` lendo `seen.json`; gravação mantendo a 1ª data e esquecendo após 90 dias; erro de publicação se o arquivo estiver corrompido; testes

## 3. CLI e docs

- [x] 3.1 CLI liga o publicador como histórico quando ele implementa a porta e informa quantas foram descartadas; README; `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam
