# Paper clássico do dia

## Why

O dono quer aprender estruturas de dados, algoritmos e design patterns com o mundo acadêmico. O arXiv cru, com os papers novos do dia sem seleção, saiu em 2026-11-28 porque não ensina. O The Morning Paper (Adrian Colyer, 2014–2021) explicou cerca de 1.000 papers clássicos, um por dia útil, com texto completo no feed. O feed oficial dá acesso ao arquivo inteiro pela paginação (`?paged=N`), sem scraping.

## What Changes

- **Tipo de fonte `rss-archive`:** lê uma página do arquivo de um feed paginado e devolve um post por dia, escolhido pela data, de modo que cada dia traz outro post e as revisões do mesmo dia trazem o mesmo.
- **Artigo atemporal:** o post do arquivo vem marcado como atemporal, e o limite de idade da edição (`max_age_days`) não vale para ele. Sem isso, um post de 2017 nunca entraria.
- **Seção "Papers"** no `journal.toml`, com o The Morning Paper como artigo. A introdução de IA dele já vem do aquecimento existente.

Fora do escopo: o arXiv filtrado por surveys e tutoriais, que espera a medição num dia útil.

## Capabilities

### New Capabilities

- `archive-source`: lê o arquivo de um feed paginado e entrega um post por dia.

### Modified Capabilities

- `article`: campo opcional `evergreen`.
- `journal-build`: o limite de idade não vale para artigos atemporais.
- `journal-config`: o tipo de fonte `rss-archive` e suas opções.

## Impact

- Código: `adapters/archive.py` (novo), `domain/article.py`, `app/build.py`, `config.py`, README.
- Uma requisição a mais por edição, ao feed do arquivo. Sem custo de IA além de um aquecimento por dia, que já está no orçamento do `[summarizer]`.
