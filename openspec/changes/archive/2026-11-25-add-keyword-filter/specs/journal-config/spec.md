## ADDED Requirements

### Requirement: Optional filter section
The configuration MAY have a `[filter]` table with `include` and `exclude` (lists of non-empty strings) and `max_articles` (positive integer), all optional. Without the table, every fetched article SHALL be published. An invalid `[filter]` SHALL be rejected with a configuration error naming the offending key.

#### Scenario: Filter from configuration
- **WHEN** a configuration declares `[filter]` with `include = ["selic"]` and `max_articles = 5`
- **THEN** builds with that configuration apply that filter and cap

#### Scenario: Invalid filter option
- **WHEN** `[filter]` has `max_articles = 0`, `include = "selic"` or an unknown key `inclde`
- **THEN** loading fails with a configuration error naming that key
