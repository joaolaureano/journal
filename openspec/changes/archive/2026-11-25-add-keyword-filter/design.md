# Design

## Context

O build hoje faz: ler fontes → deduplicar por URL → ordenar (mais recente primeiro) → publicar. O filtro entra entre deduplicar e publicar.

## Goals / Non-Goals

**Goals:** filtrar por termos e limitar a quantidade, configurado no `journal.toml`.

**Non-Goals:** filtro por fonte, expressões regulares, sinônimos, ranqueamento por relevância, LLM.

## Decisions

- **Onde fica:** `journal/app/filter.py`, com `KeywordFilter(include, exclude)` e `matches(article) -> bool`. É lógica pura (stdlib: `re`, `unicodedata`), então pertence ao core e respeita a fronteira. Sem port: não há implementação alternativa hoje.
- **Normalização:** NFKD, remove marcas combinantes, `casefold()` e colapsa espaços, tanto no texto quanto nos termos. Assim "inflação", "INFLACAO" e "Inflação" são o mesmo termo.
- **Palavra inteira:** o termo normalizado casa quando não está colado a outra letra ou dígito (`(?<!\w)termo(?!\w)`). Frases ("banco central") funcionam porque os espaços são normalizados.
- **Ordem no build:** deduplicar → filtrar → ordenar → limitar. O limite vem depois da ordenação para ficar com os mais recentes.
- **Filtro que remove tudo:** publica lista vazia. As fontes funcionaram, então não é erro de build; o site mostra "Nenhum artigo publicado."
- **Relatório:** `BuildReport` ganha `fetched` (artigos únicos lidos, antes do filtro), usado pela CLI para "published N of M articles".
- **Validação da config:** `[filter]` precisa ser tabela; `include`/`exclude` listas de strings não vazias; `max_articles` inteiro positivo (bool recusado); chaves desconhecidas recusadas.

## Risks / Trade-offs

- Termos só pegam o que está escrito: "Selic" não pega uma matéria que só fala em "juros básicos". Mitigação: listar vários termos; LLM fica para uma change futura.
- Resumos de alguns feeds (Google News, Hacker News) são curtos ou vazios, então o filtro nesses depende quase só do título.
