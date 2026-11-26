# Spec Delta

## ADDED Requirements

### Requirement: Articles page
Publishing SHALL write the edition's `artigos.html` and the site's root `artigos.html`, titled like the edition's `index.html` and listing the edition's items of kind `artigo` the same way, grouped by section with a section index. With no articles, the page SHALL say that the edition has no articles.

#### Scenario: Articles apart from news
- **WHEN** an edition with one news item and one article is published
- **THEN** `index.html` lists only the news item and `artigos.html` only the article

#### Scenario: Edition without articles
- **WHEN** an edition without articles is published
- **THEN** its `artigos.html` exists and says that there are no articles

### Requirement: News and articles tabs
Both list pages SHALL show, below the masthead, a navigation labelled "Notícias" and "Artigos" linking to `index.html` and `artigos.html` of the same folder, with `aria-current="page"` on the page's own tab.

#### Scenario: Tabs on the articles page
- **WHEN** an edition is published
- **THEN** its `artigos.html` has a link to `index.html` and a link to `artigos.html` marked `aria-current="page"`

### Requirement: Reading time of articles
On the articles page, an item with a body SHALL show its reading time after the date: the body's word count divided by 200, rounded, at least 1, as `N min de leitura`. Items without body SHALL show none.

#### Scenario: Long article
- **WHEN** an article whose body has 2,400 words is published
- **THEN** its item on `artigos.html` shows `12 min de leitura`

## MODIFIED Requirements

### Requirement: Article list page
Publishing SHALL write the edition's `index.html` and the site's front `index.html`, both titled with the edition date (`Edição de 26 nov 2026`, plus `(revisão N)` from the second revision on) and listing every item of kind `noticia` in the order received, each with its title linking to its article page, its source, its publication date and its summary. With no news, the page SHALL say so.

#### Scenario: Index lists articles in order
- **WHEN** an edition with two articles is published
- **THEN** its `index.html` shows both titles in the order received
- **AND** each title links to `articles/<id>.html` of that article inside the edition folder

#### Scenario: Empty edition
- **WHEN** an edition without articles is published
- **THEN** its `index.html` exists and states that there are no news

### Requirement: Article page
Publishing SHALL write `articles/<id>.html` in the edition folder for every article, showing its title, source, publication date, its body when it has one and otherwise its summary, a link to the original URL and a link back to the list page of its kind (`../index.html` or `../artigos.html`).

#### Scenario: Article page content
- **WHEN** an article is published
- **THEN** its page shows its title, source, date and summary
- **AND** links to the article's original URL and to `../index.html`

#### Scenario: Article page with body
- **WHEN** an article with a body of three paragraphs and a photo is published
- **THEN** its page shows the three paragraphs and the photo in place of the summary
- **AND** the edition's list page still shows the summary

#### Scenario: Back to the articles page
- **WHEN** an item of kind `artigo` is published
- **THEN** its page links back to `../artigos.html`

### Requirement: Publish order keeps the site consistent
Publishing SHALL write the edition's files first, then `style.css` and the archive, then `editions.json`, then the root `artigos.html`, and the root `index.html` last. When publishing fails midway, the root `index.html` and `editions.json` SHALL be left as they were.

#### Scenario: Publish fails midway
- **WHEN** writing an edition fails before it is complete
- **THEN** the root `index.html` and `editions.json` still describe the previous edition

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the edition folder: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` (ISO 8601 with UTC offset), `image`, `image_caption`, `image_credit`, `section` and `kind`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** an edition with two articles is published
- **THEN** the edition's `articles.json` holds two objects, in the same order, with all eleven fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped
