# Spec Delta

## MODIFIED Requirements

### Requirement: Article fields
An article SHALL carry an id, a title, a URL, a summary, a source name, a publication timestamp, an optional section name and an optional body (both absent by default), and a kind, `noticia` (the default) or `artigo`. The body is HTML that the source has already reduced to safe markup.

#### Scenario: Article created with all fields
- **WHEN** an article is created with title, URL, summary, source and publication timestamp
- **THEN** each value is readable from the article exactly as given
- **AND** the article exposes an id

#### Scenario: Empty summary is allowed
- **WHEN** an article is created with an empty summary
- **THEN** the article is created successfully

#### Scenario: Body is optional
- **WHEN** an article is created without a body
- **THEN** its body is absent

#### Scenario: Kind defaults to news
- **WHEN** an article is created without a kind
- **THEN** its kind is `noticia`

#### Scenario: Unknown kind
- **WHEN** an article is created with kind `blog`
- **THEN** creation fails with a validation error
