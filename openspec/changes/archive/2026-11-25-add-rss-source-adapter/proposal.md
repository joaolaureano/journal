# Proposal

## Why

O journal precisa de uma primeira fonte real de artigos. RSS/Atom é o formato mais comum entre portais de notícia e ciência e serve como adapter de referência para as fontes futuras (Google News, RSSHub, Reddit).

## What Changes

- Adapter de fonte RSS que lê **um** feed, cujo endereço e nome são passados na construção, e devolve `Article`s.
- Resumo convertido em texto puro (sem HTML), para o frontend não precisar confiar no conteúdo do feed.
- Entradas inválidas (sem título, link ou data) são descartadas sem derrubar o feed inteiro.
- Falhas do feed (inalcançável, lento demais, conteúdo que não é feed) viram um erro de fonte definido no core, para o caso de uso poder tratá-lo sem conhecer o adapter.
- Testes com fixture XML local, sem rede.
- Fora: múltiplos feeds e leitura por arquivo de config (change `add-config-registry`), cache/ETag, limpeza de parâmetros de rastreio na URL.

## Capabilities

### New Capabilities
- `rss-source`: como um feed RSS/Atom é lido e transformado em artigos, e como falhas do feed são reportadas.

### Modified Capabilities
- `core-boundary`: adiciona o erro de fonte ao contrato de fonte.

## Impact

- Nova dependência de runtime: `feedparser`.
- Novos módulos: `src/journal/adapters/rss.py`; `SourceError` em `src/journal/ports/source.py`.
- Novos testes e fixtures em `tests/`.
