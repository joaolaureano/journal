# Tasks

## 1. Projeto e ambiente

- [x] 1.1 Criar `pyproject.toml` (pacote `journal`, `requires-python = ">=3.12"`, build `hatchling`, layout `src/`) e verificar que `uv sync` cria `.venv` e `uv.lock` sem erro
- [x] 1.2 Adicionar `pytest` e `ruff` como dependências de dev (`uv add --dev`) e verificar que `uv run pytest --version` e `uv run ruff --version` funcionam
- [x] 1.3 Criar `.gitignore` (`.venv/`, `__pycache__/`, `dist/`, `.pytest_cache/`, `.ruff_cache/`) e verificar que `dist/` e `.venv/` estão listados

## 2. Estrutura hexagonal

- [x] 2.1 Criar `src/journal/__init__.py` e os subpacotes `domain/`, `ports/`, `adapters/`, `app/` (cada um com `__init__.py`) e verificar com `uv run python -c "import journal.domain, journal.ports, journal.adapters, journal.app"`
- [x] 2.2 Criar `tests/test_smoke.py` que importa os quatro subpacotes e verificar que `uv run pytest` passa

## 3. Lint e documentação

- [x] 3.1 Configurar ruff no `pyproject.toml` (`select = ["E", "F", "I", "B", "UP"]`, `target-version = "py312"`) e verificar que `uv run ruff check .` e `uv run ruff format --check .` passam
- [x] 3.2 Escrever `README.md` com propósito do projeto, layout das camadas e os comandos `uv sync` / `uv run pytest` / `uv run ruff check .`, e verificar executando cada comando como está escrito

## Workflow follow-up

- Arquivar a change (`openspec archive setup-project`) após validar.
- Abrir a próxima change da lista: `define-domain-and-ports` (inclui teste de fronteira: `domain` não importa `adapters`/`app`).
