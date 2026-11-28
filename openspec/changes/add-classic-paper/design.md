# Design

## Context

- `RssSource(location, name, timeout, retries, backoff, full_text)` já lê e limpa um feed, inclusive o texto completo. WordPress pagina o feed com `?paged=N`, 10 posts por página. O The Morning Paper tem 108 páginas de papers, de 2014-10 a 2021-02; a página 109 traz posts antigos do blog, de antes da série.
- O build descarta artigos mais velhos que `max_age_days` (2 dias no `journal.toml`) em `BuildJournal._in_window`, e o histórico (`seen.json`) impede repetir um item de edição anterior.
- Com `[pool]`, toda fonte passa pelo pool, que guarda só o que está na janela de 48 h pela data de publicação.

## Goals / Non-Goals

**Goals:** um paper por edição, diferente a cada dia, sem scraping e sem estado novo.

**Non-Goals:** escolher o paper pelo assunto, ou ler o arquivo inteiro de uma vez.

## Decisions

1. **`ArchiveSource` reusa o `RssSource`.** `fetch()` calcula a página e o índice a partir da data, monta a URL com `paged=<n>` (respeitando uma query que já exista) e chama um `RssSource` com `full_text=True` naquela URL. Erros de feed já saem como `SourceError`.
   - *Alternativa:* um parâmetro `archive` no `rss`. Misturaria duas formas de escolher itens num adapter só.

2. **Escolha pela data, sem estado:** com `n = date.toordinal()`, página `n % pages + 1` e post `(n // pages) % len(posts)`. Dias seguidos caem em páginas seguidas, e só depois de `pages` dias a mesma página volta, com outro post. O mesmo dia dá sempre o mesmo post, então uma revisão da edição não troca o paper. Com 108 páginas de 10 posts, são ~1.080 dias até repetir, e o histórico ainda barra um post já publicado.
   - *Alternativa:* guardar no storage quais posts já saíram. Seria estado novo para um ganho que a conta da data já dá.
   - *Atalho:* a data é a de UTC, e a edição das 08:00 de São Paulo cai às 11:00 UTC, no mesmo dia. `shortcut: usa a data UTC; passar o fuso da edição se a agenda mudar para perto da meia-noite`.

3. **`Article.evergreen`, no domínio.** O build precisa saber que aquele artigo escapa do limite de idade, e o artigo é o que chega ao build. Um campo `bool` com padrão `False` não muda nenhum artigo existente. `_in_window` passa a ignorar `max_age_days` quando `evergreen`, e mantém o corte de datas no futuro.
   - *Alternativa:* deixar o limite de idade só para notícias. Mudaria o comportamento de todos os blogs, o que ninguém pediu.

4. **Pool:** o post do arquivo é de anos atrás, então fica fora da janela de 48 h e nunca é guardado. A fonte devolve o post do dia a cada leitura, como se não houvesse pool. Nada muda no `Pooled`.

## Risks / Trade-offs

- [O blog sair do ar ou mudar a paginação] → a fonte falha como qualquer feed, e o resto da edição sai.
- [A página escolhida trazer um post que não é paper, como um anúncio] → raro no arquivo; aceito.
- [Pages fixo na config] → o arquivo está parado desde 2021, então o número não muda.
