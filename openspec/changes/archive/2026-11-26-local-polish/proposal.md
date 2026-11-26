# Proposal

## Why

Fechar as pendências locais antes de ir para a AWS: a capa é uma lista única dominada pelos feeds de alto volume, os resumos de WordPress trazem rodapé, alguns resumos são o texto inteiro, feeds WordPress não mostram imagem, os horários aparecem em UTC e faltam validações e testes pequenos.

## What Changes

- RSS: remove o rodapé do WordPress, corta o resumo em ~400 caracteres numa palavra, usa a primeira imagem do texto completo como último recurso; teste com feed Atom.
- Config: `timeout` precisa ser > 0; `section` em qualquer fonte; `[filter] max_per_section`.
- Build: artigos agrupados por seção, na ordem da config; limite por seção antes do limite geral.
- Site: blocos por seção com título; horários no fuso da edição (sem "UTC"); `section` no `articles.json`.
- Domínio: `Article.section`; `Edition.timezone`.
- `journal.toml`: seção em cada fonte, `max_age_days = 2` e `max_per_section = 10`.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `rss-source`, `article`, `edition`, `journal-build`, `journal-config`, `static-site`.

## Impact

- `adapters/rss.py`, `adapters/static_site.py`, templates, `app/build.py`, `app/sectioned.py` (novo), `config.py`, `cli.py`, domínio, `journal.toml`, README, testes.
- Fora de escopo: dedup por título entre veículos diferentes (fica para o pipeline com LLM).
