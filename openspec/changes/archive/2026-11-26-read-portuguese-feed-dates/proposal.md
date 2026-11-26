# Proposal

## Why

UOL's feeds write RFC 822 dates in Portuguese (`Qui, 26 Nov 2026 10:08:44 -0300`). feedparser does not recognise them, so every entry is skipped as having no date and the source yields nothing.

## What Changes

- When feedparser cannot parse an entry's date, the RSS source reads it as an RFC 822 date with Portuguese weekday and month abbreviations (`Seg`…`Dom`, `Jan`, `Fev`, `Mar`, `Abr`, `Mai`, `Jun`, `Jul`, `Ago`, `Set`, `Out`, `Nov`, `Dez`). Entries whose date still cannot be read are skipped as before.
- `journal.toml`: UOL Notícias (`https://rss.uol.com.br/feed/noticias.xml`) in "Brasil e mundo". Its feed only sends a cut summary, so `full_text` stays off.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `rss-source`: Portuguese RFC 822 dates are read.

## Impact

- `adapters/rss.py` (`_to_article` date fallback) and its tests; `journal.toml`.
