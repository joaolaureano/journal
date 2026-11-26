# Proposal

## Why

GZH, Jornal do Comércio e Correio do Povo vinham por busca `site:` no Google News. O build vai rodar na AWS, onde o Google News tende a responder 429/captcha; além disso, não é API oficial, os links são redirecionamentos codificados (atrapalham dedup e extração de texto) e o conteúdo é pobre (sem resumo nem imagem).

## What Changes

- Remover as três fontes do Google News do `journal.toml`.
- RS fica só com Sul21 até existir feed nativo verificado (candidato: `correiodopovo.com.br/cmlink/ultimas-1.1100282`, não testado) ou a fonte do tipo "page".

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
<!-- Nenhuma: só configuração. -->

## Impact

- `journal.toml`.
