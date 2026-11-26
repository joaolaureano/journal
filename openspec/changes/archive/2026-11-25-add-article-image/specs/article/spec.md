## ADDED Requirements

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
