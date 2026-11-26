# Proposal

## Why

Quando o servidor corta a resposta no meio da transferência (visto no g1), o urllib levanta `http.client.IncompleteRead`, que não é `OSError`. O adapter RSS não o converte em erro de fonte, então a exceção escapa do build e derruba a edição inteira por causa de um feed instável. Isso descumpre o requisito "Feed failures raise a source error".

## What Changes

- O adapter RSS converte qualquer `http.client.HTTPException` (inclui `IncompleteRead`) em erro de fonte, como já faz com erros de rede.
- Novo cenário na spec e teste com um servidor local que corta a resposta.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `rss-source`: resposta cortada passa a ser um caso explícito de erro de fonte.

## Impact

- `src/journal/adapters/rss.py`, `tests/test_rss_source.py`.
