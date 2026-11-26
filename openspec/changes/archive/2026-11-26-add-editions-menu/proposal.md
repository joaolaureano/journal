# Proposal

## Why

Para ir de uma edição a outra hoje é preciso descer até "Edições anteriores". O João quer um menu sanduíche à esquerda, fixo, com as datas das edições, e só o conteúdo do meio rolando.

## What Changes

- Toda página ganha um menu à esquerda com as 30 edições mais recentes, da mais nova para a mais antiga, em `DD/MM/AAAA` (revisões com o número: `26/11/2026 · 2`), cada uma com link para a sua pasta; a edição da página fica marcada (`aria-current="page"`). No topo, "Última edição" e, no fim, "Todas as edições".
- O menu fica fixo e tem rolagem própria; o conteúdo do meio rola como hoje.
- Aberto por padrão em telas largas; no celular começa fechado e abre por cima do conteúdo. O botão ☰ abre e fecha nos dois casos, só com CSS (caixa de seleção escondida), porque o site não usa scripts.
- O link "Edições anteriores" sai da página da edição: o menu o substitui.
- Limite: edições antigas nunca são reescritas, então o menu de uma página lista as edições que existiam quando ela foi gerada; "Última edição" e "Todas as edições" levam sempre ao estado atual.

## Impact

- `src/journal/adapters/static_site.py`, `templates/base.html`, `templates/index.html`, `templates/style.css`, `tests/test_static_site.py`, spec `static-site`.
