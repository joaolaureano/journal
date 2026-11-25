# Proposal

## Why

O caso de uso, os adapters de fonte e o publisher precisam de uma linguagem comum: o que é um artigo e quais contratos o core oferece para quem busca e quem publica artigos. Sem isso, cada adapter inventaria seu próprio formato e o core ficaria acoplado a eles.

## What Changes

- Entidade `Article` (id, title, url, summary, source, published_at) imutável, com `id` derivado de forma determinística da URL e validação mínima de invariantes.
- Port de fonte: contrato "buscar artigos" que retorna uma lista de `Article`.
- Port de publicação: contrato "publicar uma lista de artigos".
- Teste que garante a regra de dependência: `domain` e `ports` não importam `adapters`, `app` nem bibliotecas de terceiros.
- Testes dos contratos usando fakes em memória.
- Fora: `ArticleRepositoryPort` (dedup vai em memória no caso de uso; repositório só quando houver persistência entre builds).

## Capabilities

### New Capabilities
- `article`: o que constitui um artigo válido, sua identidade e imutabilidade.
- `core-boundary`: contratos de fonte e publicação expostos pelo core e a regra de que o core não depende de adapters nem de bibliotecas externas.

### Modified Capabilities
<!-- Nenhuma. -->

## Impact

- Novos módulos: `src/journal/domain/article.py`, `src/journal/ports/source.py`, `src/journal/ports/publisher.py`.
- Novos testes em `tests/`.
- Nenhuma dependência nova.
