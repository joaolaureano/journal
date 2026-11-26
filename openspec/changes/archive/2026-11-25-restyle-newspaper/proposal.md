# Proposal

## Why

O visual atual é genérico. O dono quer algo que lembre um jornal de verdade, sóbrio, sem efeitos. Das prévias, escolheu a versão "papel de jornal".

## What Changes

- Novo `style.css`: fundo creme (`#efe9dd`), tinta quase preta, fios bege; nome do jornal e manchetes em serifa; fonte, data e rótulos em monoespaçada maiúscula (estilo do portfólio do dono e do openspec.dev); coluna única de 44rem.
- Só modo claro: a cor papel é a identidade do jornal.
- Fontes do sistema, sem download (o site continua autocontido); sem animações.
- Contraste do texto secundário (`#57524b` sobre `#efe9dd`) acima de 4.5:1.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
<!-- Nenhuma: só a folha de estilo; nenhuma spec trata de aparência. A change declara skip_specs: true. -->

## Impact

- `src/journal/adapters/templates/style.css`.
