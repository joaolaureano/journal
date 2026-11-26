# Proposal

## Why

Revisão do MVP 1 apontou três lacunas que vão pesar no pipeline com LLM (cada duplicata ou notícia velha vira custo):

1. A deduplicação só pega URLs idênticas: `http`/`https`, `www.`, barra final, fragmento e parâmetros de rastreio (`utm_*`, `fbclid`...) fazem a mesma notícia aparecer duas vezes.
2. Não há janela de tempo: itens antigos de feeds lentos entram, e uma data errada no futuro fica fixa no topo.
3. Uma exceção inesperada num adapter (bug de plugin, `TypeError` no parse) derruba o build inteiro em vez de só a fonte.

## What Changes

- Dedup por chave normalizada da URL (o artigo publicado mantém a URL original).
- Nova opção `[filter] max_age_days` (inteiro positivo) e descarte, sempre, de artigos datados mais de 1 dia no futuro.
- Qualquer exceção de uma fonte vira erro de fonte no relatório; as outras seguem.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `journal-build`: dedup normalizado, janela de tempo, isolamento de falhas inesperadas.
- `journal-config`: opção `max_age_days` em `[filter]`.

## Impact

- `src/journal/app/build.py`, `src/journal/config.py`, `src/journal/cli.py`, `README.md`, testes de build e config.
- Fora de escopo: links de redirecionamento do Google News (exigiriam uma requisição por link).
