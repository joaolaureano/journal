## MODIFIED Requirements

### Requirement: Article may carry an image
An article MAY carry an image URL, an image caption and an image credit. When an image URL is given, it SHALL be an absolute http or https URL; otherwise creating the article SHALL fail with a validation error. Without them, the article's image, caption and credit SHALL be empty.

#### Scenario: Article with image
- **WHEN** an article is created with image `https://cdn.example.com/a.jpg`
- **THEN** the article's image is `https://cdn.example.com/a.jpg`

#### Scenario: Article with image caption and credit
- **WHEN** an article is created with an image, caption "Asteroid Dimorphos" and credit "ESA"
- **THEN** the article's image caption is "Asteroid Dimorphos" and its image credit is "ESA"

#### Scenario: Article without image
- **WHEN** an article is created without an image
- **THEN** the article is created and its image, caption and credit are empty

#### Scenario: Invalid image URL
- **WHEN** an article is created with image `javascript:alert(1)`
- **THEN** creation fails with a validation error
