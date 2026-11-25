# Tasks

## 1. Contrato de erro

- [x] 1.1 Adicionar `SourceError` em `src/journal/ports/source.py`, exportado em `journal.ports`, e verificar com teste em `tests/test_ports.py` que é capturável como `SourceError` (cenário de `specs/core-boundary`) e que `tests/test_core_boundary.py` continua passando

## 2. Adapter RSS

- [x] 2.1 Adicionar `feedparser` como dependência de runtime (`uv add feedparser`) e verificar `uv run python -c "import feedparser"`
- [x] 2.2 Criar fixtures `tests/fixtures/feed.xml` (RSS 2.0: itens válidos, item com HTML no resumo, item sem resumo, item só com data de atualização, item com offset não-UTC, item sem link) e `tests/fixtures/not-a-feed.html`, e verificar que os arquivos existem
- [x] 2.3 Implementar `RssSource` em `src/journal/adapters/rss.py` (download com timeout, parse, mapeamento para `Article`, texto puro, descarte de inválidos, `SourceError`) e verificar com `tests/test_rss_source.py` cobrindo todos os cenários de `specs/rss-source`, incluindo o de timeout com socket local (`uv run pytest tests/test_rss_source.py`)

## 3. Integração

- [x] 3.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar sincronizando `rss-source` (nova) e `core-boundary` (requisito adicionado).
- Abrir a próxima change: `add-build-journal-usecase`.
