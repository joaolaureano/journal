## ADDED Requirements

### Requirement: Stories from earlier days are not repeated
When a history is given, the build SHALL drop every article whose key the history reports as published before the edition's date, before applying the time window, the keyword filter and the cap, and SHALL report how many it dropped. Editions of the same date SHALL NOT count, so a later revision of a day redoes the whole day.

#### Scenario: Article already published yesterday
- **WHEN** the history reports article A as published before today and a source returns A and B
- **THEN** the publisher receives only B
- **AND** the build result reports one article already published

#### Scenario: URL variant of a published article
- **WHEN** the history reports `https://a.com/x` and a source returns `http://www.a.com/x/?utm_source=rss`
- **THEN** that article is not published
