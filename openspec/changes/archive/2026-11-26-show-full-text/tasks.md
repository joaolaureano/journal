# Tasks

## 1. Domain

- [x] 1.1 Add the optional `body: str | None = None` field to `Article` and a test that it defaults to absent

## 2. RSS source

- [x] 2.1 `full_text` option: `RssSource(full_text=False)`, the optional boolean in the `rss` type of `config.py`, and config tests (default off, invalid type)
- [x] 2.2 Write the allowlist rebuilder (`HTMLParser` subclass and a `body_html(html, base_url, skip_src)` function) in `adapters/rss.py`: allowed tags, heading shift, dropped-with-content tags, escaping, tag stack, URL resolution and http(s) check, link `rel`, image `alt`/`loading`/`referrerpolicy`, tracking-pixel drop, cover skip, trailing WordPress footer paragraph drop
- [x] 2.3 In `_to_article`, pick the longest of `content:encoded` and the summary by plain text, rebuild it and set the body only when its text is longer than the summary
- [x] 2.4 Strip hnrss.org link statistics from summaries, with tests for link and text entries
- [x] 2.5 Tests for every scenario of the rss-source delta, plus hostile inputs: `data:` URLs, attribute quote breaking, unclosed tags, nested dropped tags

## 3. Static site

- [x] 3.1 Render the body on the article page in place of the summary paragraph; keep the summary on the list page
- [x] 3.2 Styles for the body in `style.css`: readable text colour, headings, quotes, lists, images at most the column width, figure captions like the cover's
- [x] 3.3 `<meta name="robots" content="noindex, nofollow">` in `base.html`
- [x] 3.4 Tests for the static-site delta scenarios

## 4. Ship

- [x] 4.1 Ruff, the whole test suite and `openspec validate --strict`
- [x] 4.2 Preview a real edition locally (Nexo, Krebs, Netflix, O Sul) and check the pages in a screenshot
- [x] 4.3 `full_text = true` in `journal.toml` on the sources whose feeds carry the full text (measured 2026-11-26)
- [x] 4.4 Update the README, commit, push, wait for the CI deploy and publish a new edition
