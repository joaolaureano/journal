# Tasks

## 1. Fixtures

- [x] 1.1 Criar `tests/fixtures/feed2.xml` (RSS com um item de URL repetida de `feed.xml` e um item novo) e verificar que `RssSource` lê os dois itens

## 2. Configuração e registro

- [x] 2.1 Implementar `src/journal/config.py` (`ConfigError`, `AdapterType`, `SOURCE_TYPES` com `rss`, `PUBLISHER_TYPES` com `static-site`, `load_config(path)`) e verificar com `tests/test_config.py` cobrindo todos os cenários de `specs/journal-config`, incluindo registro de um tipo `fake`, e com `tests/test_core_boundary.py` passando

## 3. CLI e exemplo

- [x] 3.1 Trocar as flags do `journal build` por `--config` (default `journal.toml`) em `src/journal/cli.py`, capturando `ConfigError`; verificar com `tests/test_cli.py` reescrito para os quatro cenários de `specs/journal-build` (sucesso com duas fontes, feed com falha, falha de publicação, config inválida)
- [x] 3.2 Criar `journal.toml` na raiz (Nature e ScienceDaily, publisher `static-site` em `dist`) e atualizar `README.md` (formato da config, como adicionar uma fonte e um tipo novo); verificar executando `uv run journal build` na raiz e conferindo artigos das duas fontes em `dist/articles.json`

## 4. Integração

- [x] 4.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar sincronizando `journal-config` (nova) e `journal-build` (requisito modificado).
- Rodada MVP 1 completa; próximas changes ficam fora do escopo atual (LLM, deploy AWS).
