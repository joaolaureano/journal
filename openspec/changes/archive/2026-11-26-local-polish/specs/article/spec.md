## MODIFIED Requirements

### Requirement: Article fields
An article SHALL carry an id, a title, a URL, a summary, a source name, a publication timestamp and an optional section name (absent by default).

#### Scenario: Article created with all fields
- **WHEN** an article is created with title, URL, summary, source and publication timestamp
- **THEN** each value is readable from the article exactly as given
- **AND** the article exposes an id

#### Scenario: Empty summary is allowed
- **WHEN** an article is created with an empty summary
- **THEN** the article is created successfully
