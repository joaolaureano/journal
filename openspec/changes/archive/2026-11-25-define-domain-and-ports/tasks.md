# Tasks

## 1. Domínio

- [x] 1.1 Criar `src/journal/domain/article.py` com `Article` (dataclass frozen, `id` derivado da URL via sha256[:16], validação de título, URL http(s) e timezone) e exportá-lo em `journal.domain`; verificar com `tests/test_article.py` cobrindo todos os cenários de `specs/article` (`uv run pytest tests/test_article.py`)

## 2. Ports

- [x] 2.1 Criar `src/journal/ports/source.py` (`SourcePort`) e `src/journal/ports/publisher.py` (`PublisherPort`) como `Protocol` runtime-checkable, exportados em `journal.ports`; verificar com `tests/test_ports.py` usando fakes em memória para os cenários de contrato de `specs/core-boundary`
- [x] 2.2 Criar `tests/test_core_boundary.py` com a checagem por AST (stdlib + `journal.domain`/`journal.ports` permitidos), cobrindo o cenário de aprovação sobre o código real e o de violação com trecho sintético; verificar com `uv run pytest tests/test_core_boundary.py`

## 3. Integração

- [x] 3.0 Excluir `.agents`, `.claude` e `openspec` do ruff (o format do ruff também reescreve Markdown) e verificar que `uv run ruff format --check . -v` não lista arquivos dessas pastas
- [x] 3.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar a change sincronizando `article` e `core-boundary` para `openspec/specs/`.
- Abrir a próxima change: `add-rss-source-adapter`.
