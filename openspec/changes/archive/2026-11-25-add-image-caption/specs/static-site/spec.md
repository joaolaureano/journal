## MODIFIED Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the output directory, creating the directory if needed: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` as an ISO 8601 timestamp with UTC offset, `image` as the image URL, and `image_caption` and `image_credit`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** two articles are published to an empty output directory
- **THEN** `articles.json` holds two objects, in the same order, with all nine fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

### Requirement: Article image is shown
When an article has an image, its entry in `index.html` and its article page SHALL show it from the original URL, with an empty alternative text, lazy loading and no referrer. On the article page the image SHALL be a figure with a caption made of the image caption, when present, followed by a credit line: `Imagem: <credit>, via <source>` when the article has an image credit, otherwise `Imagem: <source>`. Articles without image SHALL render without any image element.

#### Scenario: Article with image
- **WHEN** an article with image `https://cdn.example.com/a.jpg` is published
- **THEN** `index.html` and its article page contain an `<img>` with that `src`, `alt=""`, `loading="lazy"` and `referrerpolicy="no-referrer"`

#### Scenario: Caption with credit
- **WHEN** an article from source "Ars Technica" has an image with caption "Asteroid Dimorphos" and credit "ESA"
- **THEN** its article page shows a figure caption with "Asteroid Dimorphos" and "Imagem: ESA, via Ars Technica"

#### Scenario: Caption without credit
- **WHEN** an article from source "BBC News World" has an image without caption or credit
- **THEN** its article page shows a figure caption "Imagem: BBC News World"

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** neither page contains an `<img>` or a figure caption for it
