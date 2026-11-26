# Design

## Context

`rss.py` already parses feed HTML twice with the standard library's `HTMLParser`: `_TextCollector` for plain text and `_ImgFinder` for the cover fallback. Article pages are built with `string.Template` and escape every value. The Lambda package must stay pure Python, because `deploy/build.sh` installs dependencies on the build machine for an arm64 runtime.

## Goals / Non-Goals

**Goals:**
- Show on the article page all the text and photos that the feed distributes, in their order.
- Keep pages free of scripts, frames, inline styles, event handlers and trackers.

**Non-Goals:**
- Fetching article pages (no scraping, the project rule since 2026-11-25).
- Galleries, video, embeds and tables.
- Rewriting editions already published.

## Decisions

- **Allowlist rebuild with `HTMLParser`, not a sanitizer library.** A third `HTMLParser` subclass emits a fresh document: it writes only allowed tags with allowed attributes it validated itself, and escapes all text and attribute values with `html.escape`. Nothing from the input is copied through as markup, so unknown or malformed constructs end up as escaped text or disappear. The alternatives were `nh3`, which has native wheels and so breaks the platform-free package and makes builds depend on the CI machine, and `bleach`, which is deprecated.
- **Unclosed tags are closed by the rebuilder.** It keeps a stack of open allowed tags, closes them at the end and ignores end tags that don't match an open one, so a body cannot leak an open `<blockquote>` or `<a>` into the page.
- **Longest text wins.** Some feeds put the full text in the description and nothing in `content:encoded` (Nexo, g1, Agência Brasil); others the reverse. Measuring plain text after the rebuild picks the right one without a per-source setting.
- **Body only when it adds something.** If the rebuilt plain text is no longer than the summary shown, the body is dropped, so short feeds keep today's page exactly.
- **Cover deduplication by URL** in the source, where both the cover and the body are known. Comparison is on the resolved URL.
- **Headings shift down** (h1→h2): the page's own `<h1>` is the article title.

- **`full_text` per source, off by default.** Whether a feed's text may be republished depends on the publisher's licence, which is a property of the source and not of the journal. Off by default means that a fresh or shared configuration never republishes by accident.
- **noindex as a meta tag only.** S3 cannot send arbitrary response headers, and an `X-Robots-Tag` header would need a CloudFront response headers policy, an infrastructure change for the same result on HTML pages. `robots.txt` is not used: blocking crawlers would stop them from reading the noindex.

## Risks / Trade-offs

- A parser bug could let markup through → tests feed hostile inputs (scripts, handlers, `javascript:` and `data:` URLs, unclosed tags, attribute quote breaking) and check the output with the parser itself.
- Feeds full of ads or "leia também" blocks will show them as text → acceptable; they are part of what the feed distributes, and curation can drop such sources.
- Republishing full texts on a public site → the user's decision on 2026-11-26. A password on the site was offered and declined for now.
- Photos load from the publisher's servers, as the cover already does; some may block hotlinking and show as broken images.
