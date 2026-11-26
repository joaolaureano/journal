## MODIFIED Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the edition folder: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` as an ISO 8601 timestamp with UTC offset, `image` as the image URL, `image_caption`, `image_credit` and `section`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** an edition with two articles is published
- **THEN** the edition's `articles.json` holds two objects, in the same order, with all ten fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

## REMOVED Requirements

### Requirement: Dates are shown in UTC in Portuguese
**Reason**: Readers are in the edition's timezone.
**Migration**: See "Dates are shown in the edition timezone in Portuguese".

## ADDED Requirements

### Requirement: Dates are shown in the edition timezone in Portuguese
Pages SHALL show publication dates as day, abbreviated Portuguese month, year and 24-hour time in the edition's timezone, such as `2 nov 2026, 07:00`, and SHALL also carry the full ISO 8601 timestamp in UTC in machine-readable form.

#### Scenario: Date rendering in São Paulo
- **WHEN** an article published at 2026-11-02 10:00 UTC is rendered in an edition with timezone `America/Sao_Paulo`
- **THEN** the page shows `2 nov 2026, 07:00`
- **AND** carries `2026-11-02T10:00:00+00:00` as the machine-readable date

### Requirement: Edition is grouped by section
When any article of an edition has a section, its list pages SHALL show one block per section, in the order the articles arrive, each headed by the section name; articles without section SHALL go under `Outras`. When no article has a section, the list SHALL have no section headings.

#### Scenario: Two sections and a loose article
- **WHEN** an edition holds an article of "Ciência", one of "Tecnologia" and one without section, in that order
- **THEN** the list shows the headings "Ciência", "Tecnologia" and "Outras" in that order, each above its article
