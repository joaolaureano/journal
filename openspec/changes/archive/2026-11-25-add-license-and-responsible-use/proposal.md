# Proposal

## Why

O repositório vai ficar público para que outras pessoas façam fork e montem o próprio jornal. Sem licença, o código é "todos os direitos reservados" e ninguém pode reutilizá-lo legalmente. E, como o journal reúne conteúdo de terceiros, precisa deixar claro que respeitar os termos de cada fonte e a licença de cada artigo é responsabilidade de quem o usa.

## What Changes

- Arquivo `LICENSE` com a licença MIT.
- Campo `license` no `pyproject.toml`.
- Seção "Uso responsável" no README: o journal só exibe o que cada feed distribui (título, resumo, fonte, link para o original); quem usa é responsável pelos termos das fontes e pela licença dos artigos; não baixar nem republicar texto completo, PDFs ou imagens; cuidado com resumos gerados por IA.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
<!-- Nenhuma: só licença e documentação. A change declara skip_specs: true. -->

## Impact

- `LICENSE` (novo), `pyproject.toml`, `README.md`.
