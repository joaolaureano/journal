# Proposal

## Why

Uma foto deixa a notícia mais parecida com um jornal e ajuda a reconhecer o assunto de relance. Vários feeds já trazem a imagem da matéria em campos próprios (BBC, Ars Technica, Hackaday, The Register, Tecnoblog, Nexo).

## What Changes

- O artigo ganha um campo opcional `image`: URL absoluta http(s) da imagem.
- A fonte RSS preenche `image` a partir dos campos de mídia do feed (`media:content`, `media:thumbnail`, `enclosure` de imagem). Imagens soltas dentro do HTML do resumo são ignoradas: na prática são ícones, logos e pixels de rastreamento.
- O site mostra a imagem na lista (miniatura) e na página do artigo, carregada direto do site de origem; o journal não baixa nem hospeda imagens.
- `articles.json` ganha o campo `image` (`null` quando não há).

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `article`: campo opcional `image`, validado como URL http(s).
- `rss-source`: extração da imagem dos campos de mídia.
- `static-site`: imagem nas páginas e no `articles.json`.

## Impact

- `src/journal/domain/article.py`, `src/journal/adapters/rss.py`, `src/journal/adapters/static_site.py`, templates e CSS, testes, fixtures, README (uso responsável).
- As páginas passam a carregar imagens de outros domínios, então quem abre o site faz requisições a esses sites.
