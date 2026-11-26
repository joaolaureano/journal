# Proposal

## Why

Feeds falham de forma passageira: o g1 já devolveu XML quebrado e cortou a resposta no meio, e um 5xx ou 429 costuma passar em segundos. Hoje uma falha dessas tira a fonte da edição do dia, que roda uma vez só.

## What Changes

- O adaptador RSS tenta de novo até 2 vezes, esperando 1 s e depois 2 s, quando a falha é passageira: rede, tempo esgotado, resposta cortada, HTTP 5xx, 408 ou 429, ou conteúdo que não é feed. Um HTTP 4xx definitivo (403, 404, 410…) falha na hora.
- O número de tentativas e a espera são parâmetros do adaptador (padrão 2 e 1 s), sem opção nova no `journal.toml`.
- Spec `journal-config`: o requisito do publicador de site estático, longo demais para a validação estrita, é dividido em dois — o publicador e o armazenamento local —, sem mudar comportamento.

## Impact

- `src/journal/adapters/rss.py`, `tests/test_rss_source.py`, specs `rss-source` e `journal-config`.
