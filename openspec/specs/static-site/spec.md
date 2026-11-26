# static-site Specification

## Purpose

Define o que o publicador de site estático grava no diretório de saída, para que hospedagem estática e consumidores do feed JSON possam contar com um formato estável.

## Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the edition folder: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` (ISO 8601 with UTC offset), `image`, `image_caption`, `image_credit`, `section`, `kind` and `warmup`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** an edition with two articles is published
- **THEN** the edition's `articles.json` holds two objects, in the same order, with all twelve fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

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

### Requirement: Feed text is escaped
All article text and URLs placed in pages SHALL be HTML-escaped, so markup coming from a feed is shown as text and never interpreted by the browser. The article body is the only exception: it is placed as is, because the source has already rebuilt it through the allowlist.

#### Scenario: Markup in title
- **WHEN** an article title is `<script>alert(1)</script>`
- **THEN** the pages contain `&lt;script&gt;alert(1)&lt;/script&gt;` and no `<script>` element

#### Scenario: Body markup kept
- **WHEN** an article with body `<p>Um <strong>dois</strong></p>` is published
- **THEN** its article page contains `<p>Um <strong>dois</strong></p>`

### Requirement: Site is self-contained and portable
Publishing SHALL write the stylesheet as `style.css` and as `style.<hash>.css`, `<hash>` being the first 10 hex digits of its SHA-256, and every page SHALL link `style.<hash>.css`, so a changed stylesheet is a new file that no cache holds. Pages SHALL use only relative links to other pages and to the stylesheet, declare `pt-BR` and include no scripts, so the site works from disk and from any static host.

#### Scenario: Pages use relative links
- **WHEN** a site is published
- **THEN** `style.css` and `style.<hash>.css` exist and every page references the latter with a relative path
- **AND** no page contains a `<script>` element or an absolute link to another page of the site

#### Scenario: Changed stylesheet, new file
- **WHEN** the stylesheet's content changes between two publications
- **THEN** the second publication's pages link a stylesheet file with a different name

### Requirement: Unrelated directories are never replaced
Publishing to local storage SHALL raise the publish error and leave the directory untouched when the output directory exists, is not empty and holds neither `editions.json` nor `articles.json` (a site from before editions). Storage keys SHALL never resolve outside the output directory.

#### Scenario: Output points at a directory with other files
- **WHEN** publishing to an existing directory that holds files but no `editions.json` or `articles.json`
- **THEN** publishing raises the publish error
- **AND** the directory and its files are unchanged

#### Scenario: Output is an empty directory
- **WHEN** publishing to an existing empty directory
- **THEN** the edition is published there

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

### Requirement: One folder per edition
Publishing SHALL write the edition to `edicoes/<YYYY-MM-DD>/` for the first revision of a date and `edicoes/<YYYY-MM-DD>-<N>/` for revision N, and SHALL write `style.css` at the root.

#### Scenario: First edition of a day
- **WHEN** the edition of 2026-11-26 is published to an empty site
- **THEN** its pages are in `edicoes/2026-11-26/`

### Requirement: Editions are never overwritten
Publishing an edition for a date that already has one SHALL create the next revision, leaving every earlier edition's files unchanged. A revision folder that already exists SHALL be skipped even when the manifest does not list it.

#### Scenario: Second run on the same day
- **WHEN** the edition of 2026-11-26 is published twice
- **THEN** the second goes to `edicoes/2026-11-26-2/` and the first folder is unchanged

#### Scenario: Lost manifest
- **WHEN** `edicoes/2026-11-26/` exists but `editions.json` does not list it
- **THEN** a new edition of that date goes to `edicoes/2026-11-26-2/`

### Requirement: Editions manifest
Publishing SHALL keep `editions.json` at the root: a JSON array, oldest first, with one object per edition holding `date` (ISO date), `revision`, `path` (edition folder, ending in `/`), `articles` (count) and `published_at` (UTC timestamp). A manifest that is not a JSON array SHALL make publishing fail with the publish error.

#### Scenario: Manifest after two editions
- **WHEN** editions of 2026-11-25 and 2026-11-26 are published
- **THEN** `editions.json` lists both, in that order, with their paths and article counts

### Requirement: Front page and archive
The root `index.html` SHALL show the most recently published edition, with links into its folder. `edicoes/index.html` SHALL list every edition, newest first, each linking to its folder and showing its article count.

#### Scenario: Front page follows the latest edition
- **WHEN** an edition is published after another
- **THEN** the root `index.html` lists the newer edition's articles

#### Scenario: Archive order
- **WHEN** editions of 2026-11-25 and 2026-11-26 are published
- **THEN** `edicoes/index.html` lists 26 nov before 25 nov

### Requirement: Publish order keeps the site consistent
Publishing SHALL write the edition's files first, then `style.css` and the archive, then `editions.json`, then the root `artigos.html`, and the root `index.html` last. When publishing fails midway, the root `index.html` and `editions.json` SHALL be left as they were.

#### Scenario: Publish fails midway
- **WHEN** writing an edition fails before it is complete
- **THEN** the root `index.html` and `editions.json` still describe the previous edition

### Requirement: Storage is pluggable
The static site SHALL write through a storage contract offering `exists`, `read` and `write` on relative POSIX keys, so the same site logic can publish to the local disk or to other storages. The built-in local storage SHALL write each file atomically.

#### Scenario: Local storage
- **WHEN** the static site publishes through local storage rooted at `dist`
- **THEN** the files appear under `dist` with the keys as relative paths

### Requirement: Publication history
The static site SHALL act as the journal's history through `seen.json` at the root: a JSON object mapping each published article's key to the date of the first edition that published it. Publishing SHALL add the edition's articles, keeping an existing date, SHALL drop entries more than 90 days older than the edition date, and SHALL write `seen.json` before `editions.json`. A `seen.json` that is not a JSON object SHALL make the history and publishing fail with the publish error.

#### Scenario: Earlier days only
- **WHEN** article A was published on 2026-11-25 and article B on 2026-11-26
- **THEN** the history for 2026-11-26 holds only A's key

#### Scenario: Revision keeps the first date
- **WHEN** article A was published on 2026-11-25 and again in an edition of 2026-11-26
- **THEN** `seen.json` keeps 2026-11-25 for A

#### Scenario: Retention
- **WHEN** an article was published 117 days before the latest edition
- **THEN** it is no longer in the history

### Requirement: Dates are shown in the edition timezone in Portuguese
Pages SHALL show publication dates as day, abbreviated Portuguese month, year and 24-hour time in the edition's timezone, such as `2 nov 2026, 07:00`, and SHALL also carry the full ISO 8601 timestamp in UTC in machine-readable form.

#### Scenario: Date rendering in São Paulo
- **WHEN** an article published at 2026-11-02 10:00 UTC is rendered in an edition with timezone `America/Sao_Paulo`
- **THEN** the page shows `2 nov 2026, 07:00`
- **AND** carries `2026-11-02T10:00:00+00:00` as the machine-readable date

### Requirement: Edition is grouped by section
When any article of an edition has a section, its list pages SHALL show one block per section, in the order the articles arrive, each headed by the section name; articles without section SHALL go under `Outras`. When no article has a section, the list SHALL have no section headings.

#### Scenario: Two sections and a loose article
- **WHEN** an edition holds an article of "Ciência", one of "Tecnologia" and one without section, in that order
- **THEN** the list shows the headings "Ciência", "Tecnologia" and "Outras" in that order, each above its article

### Requirement: Editions menu
Every page SHALL include a navigation menu listing the 30 most recent editions known when the page is written, newest first, each shown as `DD/MM/YYYY` (followed by ` · <revision>` for revisions after the first) and linking to its folder with a relative link, with the page's own edition marked as the current page. The menu SHALL also link to the front page and to the archive.

#### Scenario: Menu on the front page
- **WHEN** editions of 2026-11-25 and 2026-11-26 are published
- **THEN** the front page menu lists `26/11/2026` then `25/11/2026`, and marks `26/11/2026` as current

#### Scenario: Many editions
- **WHEN** 31 editions have been published
- **THEN** the menu lists the 30 most recent and links to the archive

### Requirement: Menu stays put while the content scrolls
The menu SHALL stay fixed at the left of the viewport with its own scrolling, open by default on wide screens and closed by default on narrow ones, and a menu button SHALL toggle it without scripts.

#### Scenario: Narrow screen
- **WHEN** a page is opened on a narrow screen
- **THEN** the menu is hidden until the menu button is activated

### Requirement: Section index
When an edition list page shows section headings, each heading SHALL carry an `id` made from its name (lowercase, accents removed, words joined by hyphens), and the page SHALL show, right below the edition label, one link per section in page order pointing to that heading on the same page. A page without section headings SHALL show no index.

#### Scenario: Index of an edition with sections
- **WHEN** an edition holds articles of "Ciência" and "Brasil e mundo", in that order
- **THEN** below the edition label the page links to `#ciencia` and then `#brasil-e-mundo`, and the headings carry those ids

#### Scenario: No sections
- **WHEN** no article of the edition has a section
- **THEN** the page shows no section index

### Requirement: Bare articles link to their source
In an edition's list, an article with neither summary nor image SHALL have its title link straight to its source URL instead of its article page, which is still written.

#### Scenario: Article without summary or image
- **WHEN** an edition holds an article with an empty summary and no image
- **THEN** its title in the list links to the article's source URL
- **AND** its article page still exists

### Requirement: Pages ask not to be indexed
Every page SHALL carry `<meta name="robots" content="noindex, nofollow">`, so search engines that reach the journal leave it out of their results.

#### Scenario: Robots meta tag
- **WHEN** a site is published
- **THEN** every page contains `<meta name="robots" content="noindex, nofollow">`

### Requirement: Articles page
Publishing SHALL write the edition's `artigos.html` and the site's root `artigos.html`, titled like the edition's `index.html` and listing the edition's items of kind `artigo` the same way, grouped by section with a section index. With no articles, the page SHALL say that the edition has no articles.

#### Scenario: Articles apart from news
- **WHEN** an edition with one news item and one article is published
- **THEN** `index.html` lists only the news item and `artigos.html` only the article

#### Scenario: Edition without articles
- **WHEN** an edition without articles is published
- **THEN** its `artigos.html` exists and says that there are no articles

### Requirement: News and articles tabs
Both list pages SHALL show, between the edition date and the section index, a navigation labelled "Notícias" and "Artigos" linking to `index.html` and `artigos.html` of the same folder, with `aria-current="page"` on the page's own tab.

#### Scenario: Tabs on the articles page
- **WHEN** an edition is published
- **THEN** its `artigos.html` has a link to `index.html` and a link to `artigos.html` marked `aria-current="page"`

#### Scenario: Tabs below the edition date
- **WHEN** an edition with sections is published
- **THEN** in its `index.html` the tabs come after "Edição de" and before the section index

### Requirement: Reading time of articles
On the articles page, an item with a body SHALL show its reading time after the date: the body's word count divided by 200, rounded, at least 1, as `N min de leitura`. Items without body SHALL show none.

#### Scenario: Long article
- **WHEN** an article whose body has 2,400 words is published
- **THEN** its item on `artigos.html` shows `12 min de leitura`

### Requirement: AI warm-up is shown and labelled
An item with a warm-up SHALL show it, escaped, in place of its summary on `artigos.html`, preceded by `Resumo por IA`, and on its article page above the text, labelled `Resumo gerado por IA a partir de <source>`. Items without warm-up SHALL look as before.

#### Scenario: Article with warm-up
- **WHEN** an article with summary `Do feed.` and warm-up `Da IA.` is published
- **THEN** its item on `artigos.html` shows `Da IA.` marked `Resumo por IA` and not `Do feed.`
- **AND** its page shows `Da IA.` labelled as AI-generated from its source, before its text

#### Scenario: Markup in warm-up
- **WHEN** a warm-up is `<b>x</b>`
- **THEN** the pages show `&lt;b&gt;x&lt;/b&gt;` and no `<b>` element
