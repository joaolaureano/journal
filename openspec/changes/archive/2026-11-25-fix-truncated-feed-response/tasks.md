# Tasks

## 1. Correção

- [x] 1.1 Teste com servidor local que anuncia `Content-Length` maior e fecha a conexão; confirmar que falha antes da correção
- [x] 1.2 Capturar `http.client.HTTPException` no `RssSource.fetch`; `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` passam
