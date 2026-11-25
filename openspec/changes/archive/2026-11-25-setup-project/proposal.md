# Proposal

## Why

O repositório está vazio: não há pacote Python, ambiente, lint nem testes. Todas as changes seguintes (domínio, adapters, caso de uso, frontend) precisam de uma base onde código e testes já rodem, com a separação hexagonal (domain/ports/adapters/app) definida desde o início.

## What Changes

- Criar o projeto Python (`pyproject.toml`) com pacote `journal` em layout `src/`.
- Criar os subpacotes vazios `journal.domain`, `journal.ports`, `journal.adapters`, `journal.app`.
- Configurar pytest com um teste de fumaça que importa os quatro subpacotes.
- Configurar ruff (lint + format).
- Adicionar `.gitignore` e um `README.md` curto com os comandos de setup, lint e teste.

## Capabilities

### New Capabilities
<!-- Nenhuma: change de tooling/scaffolding, sem comportamento observável. -->

### Modified Capabilities
<!-- Nenhuma. A change declara skip_specs: true. -->

## Impact

- Novos arquivos na raiz: `pyproject.toml`, `uv.lock`, `.gitignore`, `README.md`, `src/journal/**`, `tests/**`.
- Dependências de desenvolvimento: `pytest`, `ruff` (gerenciadas por `uv`).
- Fora do escopo: dependências de runtime (feedparser etc.), CLI, CI, qualquer código de domínio.
