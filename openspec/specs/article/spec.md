# article Specification

## Purpose

Define o que é um artigo no journal: os campos que todo artigo carrega, como ele é identificado e quais valores são rejeitados, independente da fonte de onde veio.

## Requirements

### Requirement: Article fields
An article SHALL carry an id, a title, a URL, a summary, a source name and a publication timestamp.

#### Scenario: Article created with all fields
- **WHEN** an article is created with title, URL, summary, source and publication timestamp
- **THEN** each value is readable from the article exactly as given
- **AND** the article exposes an id

#### Scenario: Empty summary is allowed
- **WHEN** an article is created with an empty summary
- **THEN** the article is created successfully

### Requirement: Article identity derives from URL
The article id SHALL be derived deterministically from its URL, so the same URL always yields the same id across builds and sources, and different URLs yield different ids.

#### Scenario: Same URL, same id
- **WHEN** two articles are created with the same URL but different titles or sources
- **THEN** both have the same id

#### Scenario: Different URL, different id
- **WHEN** two articles are created with different URLs
- **THEN** their ids differ

#### Scenario: Id is safe for file names
- **WHEN** an article is created
- **THEN** its id contains only lowercase hexadecimal characters

### Requirement: Article rejects invalid values
Creating an article SHALL fail when the title is blank, the URL is not an absolute http or https URL, or the publication timestamp has no timezone.

#### Scenario: Blank title
- **WHEN** an article is created with a title that is empty or only whitespace
- **THEN** creation fails with a validation error

#### Scenario: Non-http URL
- **WHEN** an article is created with a relative URL or a URL whose scheme is not http or https
- **THEN** creation fails with a validation error

#### Scenario: Naive timestamp
- **WHEN** an article is created with a publication timestamp without timezone information
- **THEN** creation fails with a validation error

### Requirement: Article is immutable
An article SHALL NOT allow its fields to be changed after creation.

#### Scenario: Attempt to change a field
- **WHEN** code tries to assign a new title to an existing article
- **THEN** the assignment fails and the article keeps its original title

### Requirement: Article may carry an image
An article MAY carry an image URL. When given, it SHALL be an absolute http or https URL; otherwise creating the article SHALL fail with a validation error. Without an image, the article's image SHALL be empty.

#### Scenario: Article with image
- **WHEN** an article is created with image `https://cdn.example.com/a.jpg`
- **THEN** the article's image is `https://cdn.example.com/a.jpg`

#### Scenario: Article without image
- **WHEN** an article is created without an image
- **THEN** the article is created and its image is empty

#### Scenario: Invalid image URL
- **WHEN** an article is created with image `javascript:alert(1)`
- **THEN** creation fails with a validation error
