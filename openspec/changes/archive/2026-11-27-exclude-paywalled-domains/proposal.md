# Excluir domínios com paywall

## Why

O feed do UOL mistura matérias da Folha, e elas ficam atrás de paywall: o leitor clica em "Ler na fonte" e não consegue ler. Os feeds não dizem quais itens são pagos, então o corte precisa ser pelo endereço do link.

## What Changes

- `[filter]` ganha `exclude_domains`: lista de domínios cujos itens não entram na edição. Vale também para os subdomínios (`folha.uol.com.br` corta `www1.folha.uol.com.br`).
- `journal.toml` exclui `folha.uol.com.br` e `folha.com.br`.
- Sai a fonte Nexo: 8 de 20 itens são pagos e nada no feed separa os pagos dos livres.

## Impact

- `app/filter.py`, `config.py`, `journal.toml`, README.
- Specs: `journal-config` (opção nova em `[filter]`) e `journal-build` (filtro por domínio).
