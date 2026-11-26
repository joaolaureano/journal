# Proposal

## Why

Hacker News e Lobsters não mandam resumo: o feed traz só um link "Comments". A página do artigo dessas notícias fica vazia (título, fonte e "Comments"), um clique a mais sem nada. Na seção Rio Grande do Sul, o Sul21 responde 403 a partir da AWS e o `/rss` do Jornal do Comércio é uma página HTML, então as duas falham todo dia na edição publicada; o O Sul tem um feed completo (resumo e imagem em quase toda notícia).

## What Changes

- Resumo que é só "Comments" vira resumo vazio.
- Na lista da edição, uma notícia sem resumo e sem imagem leva direto ao site da fonte, em vez da página do artigo, que continua sendo gerada.
- `journal.toml`: entra O Sul (`https://www.osul.com.br/feed/`) na seção Rio Grande do Sul; saem Sul21 e Jornal do Comércio. Os feeds por editoria do JC (política, geral) ficam para a revisão de curadoria.

## Impact

- `src/journal/adapters/rss.py`, `src/journal/adapters/static_site.py`, testes, `journal.toml`, specs `rss-source` e `static-site`.
