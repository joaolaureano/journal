# Tasks

## 1. Fronteira do core

- [x] 1.1 Incluir `app` em `CORE_LAYERS` de `tests/test_core_boundary.py` e ajustar o cenário de violação para cobrir import de `journal.cli` e `journal.adapters`; verificar com `uv run pytest tests/test_core_boundary.py`

## 2. Caso de uso

- [x] 2.1 Implementar `BuildJournal`, `BuildReport` e `BuildError` em `src/journal/app/build.py` (exportados em `journal.app`) e verificar com `tests/test_build.py`, usando os fakes de `tests/fakes.py`, cobrindo os cenários de agregação, falha, não-publicação, dedup e ordenação de `specs/journal-build`

## 3. Publisher estático (JSON)

- [x] 3.1 Implementar `StaticSitePublisher` em `src/journal/adapters/static_site.py` gravando `articles.json` de forma atômica e verificar com `tests/test_static_site.py` cobrindo os cenários de `specs/static-site`

## 4. CLI

- [x] 4.1 Implementar `src/journal/cli.py` (`main(argv)`, subcomando `build` com `--feed`, `--name`, `--out`) e o entry point `journal` no `pyproject.toml`; verificar com `tests/test_cli.py` (cenários de sucesso e falha do comando, usando a fixture RSS) e com `uv run journal build --feed file://$PWD/tests/fixtures/feed.xml --name Fixture --out <tmp>` gerando `articles.json`
- [x] 4.2 Documentar `journal build` no `README.md` e verificar executando o comando como está escrito

## 5. Integração

- [x] 5.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar sincronizando `journal-build` e `static-site` (novas) e `core-boundary` (requisito modificado).
- Abrir a próxima change: `add-static-frontend`.
