## MODIFIED Requirements

### Requirement: Optional filter section
The configuration MAY have a `[filter]` table with `include` and `exclude` (lists of non-empty strings), `max_articles` (positive integer) and `max_age_days` (positive integer), all optional. Without the table, no keyword filter, cap or maximum age SHALL be applied. An invalid `[filter]` SHALL be rejected with a configuration error naming the offending key.

#### Scenario: Filter from configuration
- **WHEN** a configuration declares `[filter]` with `include = ["selic"]` and `max_articles = 5`
- **THEN** builds with that configuration apply that filter and cap

#### Scenario: Maximum age from configuration
- **WHEN** a configuration declares `[filter]` with `max_age_days = 2`
- **THEN** builds with that configuration drop articles older than 2 days

#### Scenario: Invalid filter option
- **WHEN** `[filter]` has `max_articles = 0`, `max_age_days = 1.5`, `include = "selic"` or an unknown key `inclde`
- **THEN** loading fails with a configuration error naming that key
