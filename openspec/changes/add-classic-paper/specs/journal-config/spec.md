## ADDED Requirements

### Requirement: Archive source type
The `rss-archive` source type SHALL take a required `name` (string), a required `url` (string), a required `pages` (positive integer: how many archive pages the feed has) and an optional `timeout` in seconds (number greater than 0, default 10). Its articles keep the feed's full text. Like every source, it MAY have `section`, `kind` and `paths`.

#### Scenario: Classic papers
- **WHEN** a source has `type = "rss-archive"`, `url = "https://blog.acolyer.org/feed/"` and `pages = 108`
- **THEN** each edition gets one post from that archive

#### Scenario: Invalid page count
- **WHEN** an `rss-archive` source has `pages = 0`
- **THEN** loading fails with a configuration error mentioning `pages`
