# rss-source Specification

## Purpose

Lê um feed RSS ou Atom a partir de um endereço configurado e entrega seus itens como artigos do journal, reportando falhas do feed de forma uniforme.

## Requirements

### Requirement: Feed entries become articles
The RSS source SHALL be configured with a feed location and a source name, and fetching SHALL return one article per valid feed entry, in feed order, with the entry's title, link and publication date, and the configured source name.

#### Scenario: Valid feed is read
- **WHEN** the source fetches a feed with two valid entries
- **THEN** it returns two articles in the same order as the feed
- **AND** each article has the entry's title, link and publication date, and the configured source name

#### Scenario: Updated date used when published date is missing
- **WHEN** an entry has no published date but has an updated date
- **THEN** the article's publication timestamp is the updated date

#### Scenario: Dates are in UTC
- **WHEN** an entry's date is given with a non-UTC offset
- **THEN** the article's publication timestamp represents the same instant in UTC

### Requirement: Summary is plain text
The article summary SHALL be the entry's summary with HTML tags removed, HTML entities decoded and whitespace collapsed to single spaces. An entry without a summary SHALL yield an empty summary.

#### Scenario: HTML summary
- **WHEN** an entry's summary is `<p>Hello&nbsp;<b>world</b></p>\n<script>x()</script>`
- **THEN** the article summary is `Hello world`

#### Scenario: Missing summary
- **WHEN** an entry has no summary
- **THEN** the article summary is empty

### Requirement: Invalid entries are skipped
Entries missing a title, a link or a date, or whose values are rejected as an article, SHALL be skipped while the remaining entries are still returned.

#### Scenario: Entry without link
- **WHEN** a feed has three entries and one has no link
- **THEN** fetching returns the other two articles

### Requirement: Feed failures raise a source error
Fetching SHALL raise the core source error, naming the feed location, when the feed cannot be retrieved, does not answer within the configured timeout, its transfer is cut before the full response arrives, or its content is not a feed.

#### Scenario: Unreachable feed
- **WHEN** the feed location does not exist
- **THEN** fetching raises the source error

#### Scenario: Slow feed
- **WHEN** the feed server accepts the connection but does not answer within the timeout
- **THEN** fetching raises the source error instead of waiting indefinitely

#### Scenario: Truncated response
- **WHEN** the feed server announces a response length and closes the connection before sending all of it
- **THEN** fetching raises the source error

#### Scenario: Content is not a feed
- **WHEN** the feed location returns content that is not RSS or Atom
- **THEN** fetching raises the source error

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
