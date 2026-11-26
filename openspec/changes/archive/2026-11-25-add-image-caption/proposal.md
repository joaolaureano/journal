# Proposal

## Why

O dono quer legenda nas fotos, como num jornal. Além de descrever a imagem, a legenda dá o crédito, o que importa para o uso responsável de imagens de terceiros.

## What Changes

- O artigo ganha `image_caption` (descrição da foto) e `image_credit` (autor ou agência), ambos opcionais.
- A fonte RSS lê a descrição de `media:text` e o crédito de `media:credit`. `media:description` não serve: o feedparser o mistura ao resumo da notícia.
- Na página da notícia, a foto vira uma figura com legenda: a descrição, quando houver, e sempre uma linha de crédito, `Imagem: <crédito>, via <fonte>` ou `Imagem: <fonte>` quando o feed não dá o crédito.
- A miniatura da lista continua sem legenda: é pequena demais e a fonte já aparece logo abaixo do título.
- `articles.json` ganha `image_caption` e `image_credit`.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `article`: campos de legenda e crédito da imagem.
- `rss-source`: leitura de `media:text` e `media:credit`.
- `static-site`: figura com legenda na página da notícia e campos novos no JSON.

## Impact

- `src/journal/domain/article.py`, `src/journal/adapters/rss.py`, `src/journal/adapters/static_site.py`, `templates/style.css`, testes, fixture `images.xml`.
- Hoje só a Ars Technica traz descrição e crédito; nos outros feeds a legenda é só `Imagem: <fonte>`.
