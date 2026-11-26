## MODIFIED Requirements

### Requirement: Built-in RSS source type
The `rss` source type SHALL take a required `name` (string), a required `url` (string) and an optional `timeout` in seconds (number greater than 0, default 10).

#### Scenario: RSS source from configuration
- **WHEN** a source entry is `type = "rss"`, `name = "Nature"`, `url = "https://www.nature.com/nature.rss"`
- **THEN** the loaded source reads that feed and labels its articles `Nature`

### Requirement: Optional filter section
The configuration MAY have a `[filter]` table with `include` and `exclude` (lists of non-empty strings), `max_articles`, `max_age_days` and `max_per_section` (positive integers), all optional. Without the table, no keyword filter, cap or maximum age SHALL be applied. An invalid `[filter]` SHALL be rejected with a configuration error naming the offending key.

#### Scenario: Filter from configuration
- **WHEN** a configuration declares `[filter]` with `include = ["selic"]` and `max_articles = 5`
- **THEN** builds with that configuration apply that filter and cap

#### Scenario: Maximum age from configuration
- **WHEN** a configuration declares `[filter]` with `max_age_days = 2`
- **THEN** builds with that configuration drop articles older than 2 days

#### Scenario: Invalid filter option
- **WHEN** `[filter]` has `max_articles = 0`, `max_age_days = 1.5`, `include = "selic"` or an unknown key `inclde`
- **THEN** loading fails with a configuration error naming that key

## ADDED Requirements

### Requirement: Any source can belong to a section
Every source entry, whatever its type, MAY have a `section` (non-empty string) naming the section its articles belong to. Any other value SHALL be rejected with a configuration error mentioning `section`.

#### Scenario: RSS source with section
- **WHEN** an `rss` source declares `section = "Ciência"`
- **THEN** its articles belong to the section "Ciência"
