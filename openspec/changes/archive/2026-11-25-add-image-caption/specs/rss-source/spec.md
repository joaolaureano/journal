## ADDED Requirements

### Requirement: Image caption and credit come from feed media
When an entry yields an image, the article image caption SHALL be the entry's `media:text` as plain text and the image credit SHALL be the text of its first `media:credit`, each empty when missing or blank. Entries without image SHALL have neither.

#### Scenario: Caption and credit present
- **WHEN** an entry has an image, `media:text` "Asteroid <b>Dimorphos</b>" and `media:credit` "ESA"
- **THEN** the article image caption is "Asteroid Dimorphos" and its image credit is "ESA"

#### Scenario: Image without caption or credit
- **WHEN** an entry has an image but no `media:text` and no `media:credit`
- **THEN** the article has the image and empty caption and credit
