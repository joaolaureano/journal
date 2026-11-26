# Spec Delta

## MODIFIED Requirements

### Requirement: Built-in RSS source type
The `rss` source type SHALL take a required `name` (string), a required `url` (string), an optional `timeout` in seconds (number greater than 0, default 10) and an optional `full_text` (boolean, default false) that keeps the feed's full text as the article body.

#### Scenario: RSS source from configuration
- **WHEN** a source entry is `type = "rss"`, `name = "Nature"`, `url = "https://www.nature.com/nature.rss"`
- **THEN** the loaded source reads that feed and labels its articles `Nature`

#### Scenario: Full text is opt-in
- **WHEN** a source entry has no `full_text`
- **THEN** its articles have no body

#### Scenario: Invalid full_text
- **WHEN** an `rss` source has `full_text = "yes"`
- **THEN** loading fails with a configuration error naming `full_text`
