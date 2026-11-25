# Design

## Context

Repositório greenfield (só `openspec/` e skills). Destino final é AWS Lambda, então a versão de Python precisa ser suportada pelo runtime gerenciado. Na máquina já existem `uv` e Python 3.12–3.14.

## Goals / Non-Goals

**Goals:**
- `uv sync`, `uv run pytest` e `uv run ruff check` funcionando do zero.
- Pacote importável `journal` com os quatro subpacotes da arquitetura hexagonal.

**Non-Goals:**
- Checagem automática de fronteira entre camadas (entra junto com o domínio na change `define-domain-and-ports`).
- Type checker (mypy/pyright), pre-commit, CI.

## Decisions

- **uv em vez de pip/poetry**: já instalado, gera lockfile, cuida da versão do Python. Alternativa poetry: mais uma ferramenta sem ganho aqui.
- **Python `>=3.12`**: suportado pelo Lambda e disponível localmente; sem motivo para fixar em algo mais novo agora.
- **Layout `src/journal/`**: evita importar o pacote por acidente a partir da raiz nos testes; nome `journal` casa com a CLI futura `journal build`.
- **ruff para lint e format**: uma ferramenta substitui flake8+isort+black. Regras: padrão + `I` (isort), `B`, `UP`.
- **Build backend `hatchling`**: padrão do `uv init --package`, sem configuração extra.

## Risks / Trade-offs

- [Nome `journal` genérico pode colidir com outro pacote no futuro repo público] → Renomear é barato enquanto o projeto é pequeno; decidir na separação público/privado.
