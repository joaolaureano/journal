# Proposal

## Why

Com 23 fontes, um build publica perto de mil notícias, e a meta do jornal é poucas por dia. Falta um jeito de escolher o que entra (por exemplo, só notícias de finanças) e de limitar quantas são publicadas, sem LLM e sem código por fonte.

## What Changes

- Nova seção opcional `[filter]` no `journal.toml`:
  - `include`: lista de termos; se houver, só entram artigos com pelo menos um deles no título ou no resumo.
  - `exclude`: lista de termos; artigos com qualquer um deles saem, mesmo que casem com `include`.
  - `max_articles`: publica só os N mais recentes depois do filtro.
- A comparação ignora maiúsculas e acentos e casa palavras ou frases inteiras ("juros" não casa com "conjuros").
- O comando `journal build` passa a dizer quantos artigos foram publicados de quantos foram lidos ("published 5 of 996 articles").
- Sem `[filter]`, o comportamento atual não muda.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `journal-build`: o build aplica o filtro e o limite antes de publicar.
- `journal-config`: a configuração aceita a seção `[filter]`.

## Impact

- `src/journal/app/` (filtro e build), `src/journal/config.py`, `src/journal/cli.py`, testes, README.
- O filtro fica no core (só stdlib): não é um adapter, porque não fala com nada externo. Um filtro por LLM no futuro seria um port novo.
