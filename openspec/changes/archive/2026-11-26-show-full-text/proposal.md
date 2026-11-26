# Proposal

## Why

Many feeds already ship the whole story (Nexo, Agência Brasil, g1, O Sul, Poder360, Krebs, Cloudflare, Netflix, Julia Evans, Fowler and others, from 1,200 to 16,000 characters), with photos in the middle of the text, but the journal cuts every summary at 400 characters and keeps only one cover image. The article page then shows a fragment of a text the feed gave us in full.

## What Changes

- A new `full_text` option of the `rss` source (off by default) turns the body on for that source. When on, the RSS source keeps the longest text the entry carries (`content:encoded` or the summary) as the article **body**: feed HTML rebuilt through an allowlist, with paragraphs, headings, lists, quotes, links and photos in their place, captions included.
- Everything outside the allowlist is dropped: scripts, styles, frames, embeds, forms, event handlers, styles and classes, and tracking pixels (images 1–2 px wide or tall). Links and images keep only absolute http(s) URLs, with relative ones resolved against the article URL.
- The photo already shown as the cover is not repeated in the body, and the WordPress footer ("O post … apareceu primeiro em …") is removed from it.
- The article page shows the body in place of the summary when there is one. The edition list stays as it is: title, the summary cut at 400 characters, one thumbnail.
- Every page carries `<meta name="robots" content="noindex, nofollow">`, so search engines that reach the public site leave it out.
- hnrss.org's link statistics ("Article URL: …", "Comments URL: …", "Points: …") are no longer shown as a summary, so Hacker News Best items become bare links like Hacker News and Lobsters.
- Feeds that only send a short summary (BBC, Folha, ScienceDaily, InfoQ, Correio do Povo) are unchanged. The journal still reads only what feeds distribute: no page downloads.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `article`: an article may carry an optional body (sanitized HTML).
- `journal-config`: the `rss` source type takes an optional `full_text` boolean.
- `rss-source`: with `full_text`, the body comes from the entry's longest text, rebuilt through an allowlist; hnrss statistics are removed from summaries.
- `static-site`: pages ask not to be indexed; the article page shows the body; the body is the one piece of feed markup a page keeps, and only after the allowlist.

## Impact

- Code: `domain/article.py` (field `body`), `adapters/rss.py` (body choice and the allowlist rebuild, on the standard library's `HTMLParser` like the existing text and image parsers), `adapters/static_site.py`, `templates/article.html`, `templates/style.css`.
- No new dependency: the Lambda package stays pure Python (`deploy/build.sh` builds for arm64 from any machine).
- Article pages grow (a body is up to a few tens of KB). `articles.json` is unchanged.
- The site stays public (the user's decision of 2026-11-26). `full_text` is off by default so that a public deployment republishes only the sources whose licence allows it; this journal turns it on for the sources whose feeds carry the full text.
- `journal.toml`: `full_text = true` on the sources whose feeds carry the full text.
- Editions already published keep their short pages.
