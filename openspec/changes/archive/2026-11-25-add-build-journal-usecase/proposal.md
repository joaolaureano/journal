# Proposal

## Why

Já existem artigos, contratos e uma fonte RSS, mas nada os junta. Falta o caso de uso que transforma "várias fontes" em "uma lista publicada": buscar, remover duplicatas, ordenar e publicar, e um comando para rodá-lo localmente (e depois no Lambda).

## What Changes

- Caso de uso `BuildJournal`: busca em todas as sources, tolera falha de uma fonte, remove duplicatas por URL, ordena do mais recente para o mais antigo e entrega ao publisher.
- Se nenhuma fonte entregar artigos com sucesso, o build falha **sem publicar**, para não apagar um site já publicado.
- CLI `journal build --feed URL --name NOME [--out DIR]`, com código de saída e resumo do que foi publicado. As flags são provisórias até a change `add-config-registry`.
- Primeiro publisher concreto: site estático que grava `articles.json` no diretório de saída (o HTML vem na change `add-static-frontend`).
- A regra de dependência do core passa a cobrir também a camada `app`.

## Capabilities

### New Capabilities
- `journal-build`: regras de agregação (falhas, dedup, ordenação, quando publicar) e o comando `journal build`.
- `static-site`: o que o publisher estático grava no diretório de saída.

### Modified Capabilities
- `core-boundary`: a camada `app` também não pode depender de adapters nem de bibliotecas externas.

## Impact

- Novos módulos: `src/journal/app/build.py`, `src/journal/adapters/static_site.py`, `src/journal/cli.py`.
- `pyproject.toml`: entry point `journal`.
- Teste de fronteira atualizado para incluir `app`.
