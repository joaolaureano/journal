## ADDED Requirements

### Requirement: Entry image comes from feed media
The article image SHALL be the first absolute http or https URL among, in order: the entry's media content items that are images (medium `image`, an `image/*` type, or no declared type), its media thumbnails and its enclosures with an `image/*` type. Images inside the summary HTML SHALL NOT be used. An entry without a usable image SHALL still become an article, without image.

#### Scenario: Media thumbnail
- **WHEN** an entry has a `media:thumbnail` with URL `https://cdn.example.com/t.jpg`
- **THEN** the article image is `https://cdn.example.com/t.jpg`

#### Scenario: Image enclosure
- **WHEN** an entry has an enclosure of type `image/jpeg`
- **THEN** the article image is the enclosure URL

#### Scenario: Non-image enclosure
- **WHEN** an entry's only enclosure has type `audio/mpeg`
- **THEN** the article has no image

#### Scenario: Image only in summary HTML
- **WHEN** an entry's only image is an `<img>` inside its summary
- **THEN** the article has no image

#### Scenario: Invalid image URL is dropped
- **WHEN** an entry's only media URL is not http or https
- **THEN** the article is still returned, without image
