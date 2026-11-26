## MODIFIED Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the output directory, creating the directory if needed: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` as an ISO 8601 timestamp with UTC offset, and `image` as the image URL or `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** two articles are published to an empty output directory
- **THEN** `articles.json` holds two objects, in the same order, with all seven fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

## ADDED Requirements

### Requirement: Article image is shown
When an article has an image, its entry in `index.html` and its article page SHALL show it from the original URL, with an empty alternative text, lazy loading and no referrer. Articles without image SHALL render without any image element.

#### Scenario: Article with image
- **WHEN** an article with image `https://cdn.example.com/a.jpg` is published
- **THEN** `index.html` and its article page contain an `<img>` with that `src`, `alt=""`, `loading="lazy"` and `referrerpolicy="no-referrer"`

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** neither page contains an `<img>` for it
