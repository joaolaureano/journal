# Proposal

## Why

An edition mixes two ways of reading: news to skim, and articles (blog posts, essays, long reports) to choose and read calmly. Today both share one list, so a Martin Fowler essay sits between a g1 headline and a NASA note, and busy news sources push articles out of shared sections.

## What Changes

- Every source MAY declare `kind = "artigo"` (default `"noticia"`), like `section`. Articles carry their kind.
- Each edition gets two list pages: `index.html` with the news and `artigos.html` with the articles, each grouped by section with its own section index. Tabs "Notícias" and "Artigos" below the masthead switch between them, with plain links (no scripts). The site root gets `artigos.html` too.
- On the articles page, items with a body show the reading time ("12 min de leitura").
- The per-section cap counts news and articles of a section separately.
- An article page links back to the list page of its kind. `articles.json` gains `kind`.
- `journal.toml`: the blogs, The Conversation Brasil, Pesquisa FAPESP, IEEE Spectrum, Krebs and Agência Pública become articles.
- Out of scope (next step): different rules for articles (longer age window, relevance instead of recency, a small daily quota).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `article`: an article has a kind, news or article.
- `journal-config`: any source may declare its kind.
- `journal-build`: the per-section cap applies per section and kind.
- `static-site`: news and articles pages with tabs, reading time, back link by kind, publish order, `kind` in `articles.json`.
- `aws-deploy`: the root `artigos.html` gets the short cache.

## Impact

- Code: `domain/article.py`, `app/sectioned.py` (also sets the kind), `config.py`, `app/build.py`, `adapters/static_site.py`, `adapters/s3.py`, templates and `style.css`.
- Editions already published keep a single list and no tabs; the menu links still open their `index.html`.
