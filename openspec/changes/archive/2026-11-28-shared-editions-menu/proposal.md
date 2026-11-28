# Menu de edições compartilhado e navegação em duas linhas

## Why

O dono abriu uma edição antiga e o menu só listava ela e as anteriores: cada página grava o menu quando é publicada, e edições antigas nunca são reescritas. Na capa nova, ele também pediu as abas Notícias/Artigos numa linha e as seções na linha de baixo.

## What Changes

- **Menu compartilhado:** o menu de edições vira um arquivo só, `menu.html` na raiz, regravado a cada edição e mostrado em todas as páginas por um `iframe`, sem script. A edição da página continua marcada, pela âncora da URL do `iframe` (`menu.html#e-<pasta>`) e `:target` no CSS. Os links abrem na janela inteira.
- **Navegação em duas linhas:** abas numa linha, índice de seções na de baixo; no celular, as seções rolam na horizontal.

As páginas já publicadas continuam com o menu antigo; trocar o delas é uma migração à parte, com o OK do dono.

## Capabilities

### Modified Capabilities

- `static-site`: menu de edições compartilhado.
