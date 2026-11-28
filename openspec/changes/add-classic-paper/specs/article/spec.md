## ADDED Requirements

### Requirement: Evergreen articles
An article SHALL accept an optional `evergreen` flag, false by default, marking a timeless piece, such as a classic paper explained years ago, that still belongs in today's edition.

#### Scenario: Default article
- **WHEN** an article is created without `evergreen`
- **THEN** it is not evergreen
