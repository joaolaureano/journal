# Design

## Context

`section` is already a cross-cutting source option: `config._source` pops it and wraps the adapter in `app.Sectioned`, which stamps it on every article. The static site renders one list page per edition from `_edition_page`, groups by section with `itertools.groupby` over articles already sorted by section, and has no scripts.

## Goals / Non-Goals

**Goals:**
- Read news and articles on separate pages of the same edition, switched by tabs.
- Keep articles from being crowded out by busy news sources in shared sections.

**Non-Goals:**
- Different selection rules for articles (age window, relevance, quota): the next change.
- Rewriting editions already published.

## Decisions

- **Kind is a source option handled like `section`.** `Sectioned` takes an optional kind too and stamps both, so any adapter type gets it for free. The values are Portuguese words (`noticia`, `artigo`), matching section names and the site's language.
- **Kind lives on `Article`**, validated there like the other fields, so the build (cap) and the site (pages) read it without knowing about sources.
- **Two static pages, not a toggle.** Tabs are plain links to `index.html` and `artigos.html` in the same folder, so they work from disk and with no scripts, like the rest of the site. The menu keeps linking each edition's `index.html`.
- **Cap per section and kind.** The cap key becomes `(section, kind)`, so three NASA notes no longer push a Pesquisa FAPESP article out of "Ciência".
- **Reading time from the body** with a tag-stripping regex: the body is markup the source already rebuilt, so tags are well formed and a regex is enough. 200 words per minute, rounded, at least 1.
- **Root `artigos.html` before root `index.html`** in the publish order, and on the short S3 cache with `index.html`.

## Risks / Trade-offs

- An edition may have no articles on quiet days → its page says so; the tab stays, so the layout does not jump.
- The archive still counts "artigos" for all items → wording left as is; it counts everything the edition holds.
