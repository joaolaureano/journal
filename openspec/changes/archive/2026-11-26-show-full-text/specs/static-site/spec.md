# Spec Delta

## ADDED Requirements

### Requirement: Pages ask not to be indexed
Every page SHALL carry `<meta name="robots" content="noindex, nofollow">`, so search engines that reach the journal leave it out of their results.

#### Scenario: Robots meta tag
- **WHEN** a site is published
- **THEN** every page contains `<meta name="robots" content="noindex, nofollow">`

## MODIFIED Requirements

### Requirement: Article page
Publishing SHALL write `articles/<id>.html` in the edition folder for every article, showing its title, source, publication date, its body when it has one and otherwise its summary, a link to the original URL and a link back to the edition's list page.

#### Scenario: Article page content
- **WHEN** an article is published
- **THEN** its page shows its title, source, date and summary
- **AND** links to the article's original URL and to `../index.html`

#### Scenario: Article page with body
- **WHEN** an article with a body of three paragraphs and a photo is published
- **THEN** its page shows the three paragraphs and the photo in place of the summary
- **AND** the edition's list page still shows the summary

### Requirement: Feed text is escaped
All article text and URLs placed in pages SHALL be HTML-escaped, so markup coming from a feed is shown as text and never interpreted by the browser. The article body is the only exception: it is placed as is, because the source has already rebuilt it through the allowlist.

#### Scenario: Markup in title
- **WHEN** an article title is `<script>alert(1)</script>`
- **THEN** the pages contain `&lt;script&gt;alert(1)&lt;/script&gt;` and no `<script>` element

#### Scenario: Body markup kept
- **WHEN** an article with body `<p>Um <strong>dois</strong></p>` is published
- **THEN** its article page contains `<p>Um <strong>dois</strong></p>`
