# Proposal

## Why

Articles should include papers, not only essays and reports. arXiv's RSS feeds send each paper's whole abstract (about 1,500 characters), but prefix it with `arXiv:<id> Announce Type: <type> Abstract:` and re-announce old papers whenever a new version is posted (`replace`, `replace-cross`: 34 of 75 entries in a sample). Hacker News, Hacker News Best and Lobsters send only links, never text.

## What Changes

- The RSS source removes the arXiv announcement prefix from summaries and bodies, and skips entries announced as `replace` or `replace-cross`.
- `journal.toml`: an "arXiv" source with cs.SE, cs.DC, cs.DB and cs.PL in a new "Papers" section, as articles with `full_text`; Hacker News, Hacker News Best and Lobsters leave.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `rss-source`: arXiv announcement entries are cleaned and replacements skipped.

## Impact

- `adapters/rss.py` and its tests; `journal.toml`; README (sources are not listed there, only behaviour).
