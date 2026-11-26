## ADDED Requirements

### Requirement: Articles can be filtered by keywords
When a keyword filter is configured, the build SHALL publish only articles whose title or summary contains at least one `include` term, when `include` terms are given, and none of the `exclude` terms. Terms SHALL match whole words or phrases, ignoring case and accents. When the filter leaves no articles, the build SHALL still succeed and publish an empty list.

#### Scenario: Include term
- **WHEN** the filter includes `selic` and articles are titled "Copom mantém a Selic" and "Time vence clássico"
- **THEN** the publisher receives only "Copom mantém a Selic"

#### Scenario: Case and accents are ignored
- **WHEN** the filter includes `inflacao` and an article summary mentions "INFLAÇÃO"
- **THEN** the article is published

#### Scenario: Whole words only
- **WHEN** the filter includes `juros` and an article is titled "Conjuros antigos"
- **THEN** the article is not published

#### Scenario: Exclude wins over include
- **WHEN** the filter includes `banco` and excludes `futebol`, and an article is titled "Banco patrocina time de futebol"
- **THEN** the article is not published

#### Scenario: Filter removes everything
- **WHEN** sources return articles and none matches the filter
- **THEN** the build succeeds and the publisher receives an empty list

### Requirement: Number of published articles can be capped
When a maximum number of articles is configured, the build SHALL publish at most that many articles, keeping the newest after filtering and ordering.

#### Scenario: Cap keeps the newest
- **WHEN** the maximum is 2 and three articles published at 09:00, 10:00 and 11:00 pass the filter
- **THEN** the publisher receives the 11:00 and 10:00 articles
