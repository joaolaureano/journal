## MODIFIED Requirements

### Requirement: Summary is plain text
The article summary SHALL be the entry's summary with HTML tags removed, HTML entities decoded and whitespace collapsed to single spaces. A trailing WordPress footer ("O post … apareceu primeiro em …" or "The post … appeared first on …") SHALL be removed. A summary longer than 400 characters SHALL be cut at the last word boundary within that limit and end with `…`. An entry without a summary SHALL yield an empty summary.

#### Scenario: HTML summary
- **WHEN** an entry's summary is `<p>Hello&nbsp;<b>world</b></p>\n<script>x()</script>`
- **THEN** the article summary is `Hello world`

#### Scenario: Missing summary
- **WHEN** an entry has no summary
- **THEN** the article summary is empty

#### Scenario: WordPress footer
- **WHEN** an entry's summary is `<p>Prédio novo</p><p>O post <a>X</a> apareceu primeiro em <a>Y</a>.</p>`
- **THEN** the article summary is `Prédio novo`

#### Scenario: Long summary
- **WHEN** an entry's summary has 800 characters of words
- **THEN** the article summary has at most 401 characters and ends with `…`

### Requirement: Entry image comes from feed media
The article image SHALL be the first absolute http or https URL among, in order: the entry's media content items that are images (medium `image`, an `image/*` type, or no declared type), its media thumbnails, its enclosures with an `image/*` type and, last, the first `<img>` of the entry's full content (`content:encoded` or Atom content). Images inside the summary HTML SHALL NOT be used. An entry without a usable image SHALL still become an article, without image.

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

#### Scenario: Image only in full content
- **WHEN** an entry has no media fields and its `content:encoded` starts with `<img src="https://wp.example.com/a.webp">`
- **THEN** the article image is `https://wp.example.com/a.webp`

## ADDED Requirements

### Requirement: Atom feeds are read
Atom feeds SHALL be read like RSS feeds: entry title, alternate link, summary and published or updated date become the article.

#### Scenario: Atom entry
- **WHEN** an Atom feed has one entry with title, alternate link, summary and updated date
- **THEN** the source returns one article with those values
