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

### Requirement: Image caption and credit come from feed media
When an entry yields an image, the article image caption SHALL be the entry's `media:text` as plain text and the image credit SHALL be the text of its first `media:credit`, each empty when missing or blank. Entries without image SHALL have neither.

#### Scenario: Caption and credit present
- **WHEN** an entry has an image, `media:text` "Asteroid <b>Dimorphos</b>" and `media:credit` "ESA"
- **THEN** the article image caption is "Asteroid Dimorphos" and its image credit is "ESA"

#### Scenario: Image without caption or credit
- **WHEN** an entry has an image but no `media:text` and no `media:credit`
- **THEN** the article has the image and empty caption and credit

### Requirement: Atom feeds are read
Atom feeds SHALL be read like RSS feeds: entry title, alternate link, summary and published or updated date become the article.

#### Scenario: Atom entry
- **WHEN** an Atom feed has one entry with title, alternate link, summary and updated date
- **THEN** the source returns one article with those values

### Requirement: Transient feed failures are retried
Fetching SHALL retry a feed up to a configurable number of extra attempts (default 2), waiting a growing delay between them (default 1 s, then 2 s), when the failure is transient: a network error or timeout, a cut transfer, an HTTP status 5xx, 408 or 429, or content that is not a feed. Any other HTTP 4xx status SHALL fail at once. When every attempt fails, fetching SHALL raise the source error of the last attempt.

#### Scenario: Server error then success
- **WHEN** the feed server answers 503 and then the feed
- **THEN** fetching returns the feed's articles

#### Scenario: Not found is not retried
- **WHEN** the feed server answers 404
- **THEN** fetching raises the source error after a single request

#### Scenario: Persistent failure
- **WHEN** the feed server answers 500 to every request
- **THEN** fetching raises the source error after the initial attempt and every retry

### Requirement: Comments-only summary is empty
A summary whose plain text is only the word "Comments" (any case), as aggregators such as Hacker News and Lobsters send, SHALL yield an empty summary. The link statistics that hnrss.org sends ("Article URL: …", "Comments URL: …", "Points: …", "# Comments: …") SHALL be removed from the summary, keeping any other text.

#### Scenario: Aggregator entry
- **WHEN** an entry's summary is `<a href="https://news.example/item?id=1">Comments</a>`
- **THEN** the article summary is empty

#### Scenario: hnrss link entry
- **WHEN** an entry's summary is `<p>Article URL: <a href="https://a.com">https://a.com</a></p><p>Comments URL: <a href="https://news.ycombinator.com/item?id=1">https://news.ycombinator.com/item?id=1</a></p><p>Points: 294</p><p># Comments: 160</p>`
- **THEN** the article summary is empty

#### Scenario: hnrss text entry
- **WHEN** an entry's summary is `<p>Como vocês testam isso?</p><hr><p>Comments URL: <a href="https://news.ycombinator.com/item?id=2">https://news.ycombinator.com/item?id=2</a></p><p>Points: 12</p><p># Comments: 3</p>`
- **THEN** the article summary is `Como vocês testam isso?`

### Requirement: Body keeps the entry's full text
When the source is configured with `full_text`, the article body SHALL be the longest of the entry's `content:encoded` values and its summary, measured as plain text, after the allowlist rebuild. The body SHALL be absent when it adds nothing to the summary: its plain text is no longer than the summary and it holds no image.

#### Scenario: Full text in content:encoded
- **WHEN** an entry has a 100-character summary and a `content:encoded` of three paragraphs with 2,000 characters
- **THEN** the article body holds the three paragraphs
- **AND** the article summary is still the 100-character summary

#### Scenario: Full text in the summary
- **WHEN** an entry has no `content:encoded` and an HTML summary of 1,500 characters
- **THEN** the article summary is cut at 400 characters
- **AND** the article body holds the whole summary as markup

#### Scenario: Source without full_text
- **WHEN** a source without `full_text` reads an entry with a 2,000-character `content:encoded`
- **THEN** the article has no body

#### Scenario: Nothing beyond the summary
- **WHEN** an entry's only text is a 200-character summary
- **THEN** the article has no body

### Requirement: Body is tidied
A text with line breaks or `<br>` and no paragraph tags SHALL become one paragraph per line. A trailing WordPress footer paragraph SHALL be dropped from the body, and so SHALL the image already used as the article image.

#### Scenario: Plain-text lines become paragraphs
- **WHEN** an entry's full text is `<img src="https://c.com/a.jpg" /><br /> Primeira linha\nSegunda linha`
- **THEN** the body is `<p>` with the image, then `<p>Primeira linha</p><p>Segunda linha</p>`

#### Scenario: Cover not repeated
- **WHEN** an entry's article image is `https://cdn.example.com/a.jpg` and its full text starts with `<img src="https://cdn.example.com/a.jpg">`
- **THEN** the body contains no image with that address

### Requirement: Body markup is rebuilt through an allowlist
The body SHALL be rebuilt from parsed feed HTML, never passed through. It SHALL keep only the tags p, br, h2–h4 (h1 as h2, h5–h6 as h4), ul, ol, li, blockquote, pre, code, strong, em, b, i, sub, sup, figure, figcaption, a with `href` and img with `src` and `alt`. Script, style, iframe, object, embed, form, svg, video, audio, noscript, template, button, select and textarea SHALL be dropped with their content; other tags SHALL be dropped and their text kept. Text SHALL be escaped.

#### Scenario: Script and handlers removed
- **WHEN** the full text is `<p onclick="x()">Oi <script>alert(1)</script><iframe src="https://e.com"></iframe></p>`
- **THEN** the body is `<p>Oi </p>`

#### Scenario: Unknown tags unwrapped
- **WHEN** the full text is `<div class="x"><span style="color:red">texto</span></div>`
- **THEN** the body contains `texto` and no div, span, class or style

### Requirement: Body links and images are safe
In the body, `href` and `src` SHALL be resolved against the article URL and kept only when the result is an absolute http(s) URL; a link or image without one SHALL lose the attribute or the image. Links SHALL get `rel="noopener noreferrer"`. Images SHALL get `loading="lazy"`, `referrerpolicy="no-referrer"` and an `alt` (empty when absent). Images whose `width` or `height` is 2 or less SHALL be dropped as tracking pixels.

#### Scenario: Relative image resolved
- **WHEN** an article at `https://site.com/n/1` has `<img src="/f/a.jpg">` in its full text
- **THEN** the body has `<img src="https://site.com/f/a.jpg" alt="" loading="lazy" referrerpolicy="no-referrer">`

#### Scenario: Script link removed
- **WHEN** the full text has `<a href="javascript:alert(1)">clique</a>`
- **THEN** the body has `<a rel="noopener noreferrer">clique</a>`

#### Scenario: Tracking pixel dropped
- **WHEN** the full text has `<img src="https://t.com/p.gif" width="1" height="1">`
- **THEN** the body has no image

### Requirement: Portuguese feed dates are read
When feedparser cannot parse an entry's published or updated date, the RSS source SHALL read it as an RFC 822 date whose weekday and month may be Portuguese abbreviations (`Seg`, `Ter`, `Qua`, `Qui`, `Sex`, `Sáb`, `Dom`; `Fev`, `Abr`, `Mai`, `Ago`, `Set`, `Out`, `Dez` besides the English ones). An entry whose date still cannot be read SHALL be skipped as having no date.

#### Scenario: UOL date
- **WHEN** an entry's date is `Qui, 26 Nov 2026 10:08:44 -0300`
- **THEN** the article's publication timestamp is 2026-11-26 13:08:44 UTC

#### Scenario: Portuguese month
- **WHEN** an entry's date is `Sáb, 05 Dez 2026 08:00:00 -0300`
- **THEN** the article's publication timestamp is 2026-12-05 11:00:00 UTC

#### Scenario: Unreadable date
- **WHEN** an entry's date is `ontem à tarde`
- **THEN** the entry is skipped

### Requirement: arXiv announcements are cleaned
The RSS source SHALL remove a leading `arXiv:<id> Announce Type: <type>` line and `Abstract:` label from the entry's text before building the summary and the body, and SHALL skip entries whose arXiv announce type is `replace` or `replace-cross`, which re-announce papers already published.

#### Scenario: New paper
- **WHEN** an entry's summary is `arXiv:2611.33159v1 Announce Type: new \nAbstract: Normal Distributions Transform scan matching…`
- **THEN** the article summary starts with `Normal Distributions Transform`

#### Scenario: Replacement skipped
- **WHEN** an entry's arXiv announce type is `replace`
- **THEN** the source returns no article for it
