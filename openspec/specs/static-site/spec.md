# static-site Specification

## Purpose

Define o que o publicador de site estático grava no diretório de saída, para que hospedagem estática e consumidores do feed JSON possam contar com um formato estável.

## Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the edition folder: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` as an ISO 8601 timestamp with UTC offset, `image` as the image URL, and `image_caption` and `image_credit`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** an edition with two articles is published
- **THEN** the edition's `articles.json` holds two objects, in the same order, with all nine fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

### Requirement: Article list page
Publishing SHALL write the edition's `index.html` and the site's front `index.html`, both titled with the edition date (`Edição de 26 nov 2026`, plus `(revisão N)` from the second revision on) and listing every article in the order received, each with its title linking to its article page, its source, its publication date and its summary, plus a link to the editions archive. With no articles, the page SHALL say that there are no articles.

#### Scenario: Index lists articles in order
- **WHEN** an edition with two articles is published
- **THEN** its `index.html` shows both titles in the order received
- **AND** each title links to `articles/<id>.html` of that article inside the edition folder

#### Scenario: Empty edition
- **WHEN** an edition without articles is published
- **THEN** its `index.html` exists and states that there are no articles

### Requirement: Article page
Publishing SHALL write `articles/<id>.html` in the edition folder for every article, showing its title, source, publication date and summary, a link to the original URL and a link back to the edition's list page.

#### Scenario: Article page content
- **WHEN** an article is published
- **THEN** its page shows its title, source, date and summary
- **AND** links to the article's original URL and to `../index.html`

### Requirement: Dates are shown in UTC in Portuguese
Pages SHALL show publication dates as day, abbreviated Portuguese month, year and 24-hour time in UTC, such as `2 nov 2026, 10:00 UTC`, and SHALL also carry the full ISO 8601 timestamp in machine-readable form.

#### Scenario: Date rendering
- **WHEN** an article published at 2026-11-02 10:00 UTC is rendered
- **THEN** the page shows `2 nov 2026, 10:00 UTC`
- **AND** carries `2026-11-02T10:00:00+00:00` as the machine-readable date

### Requirement: Feed text is escaped
All article text and URLs placed in pages SHALL be HTML-escaped, so markup coming from a feed is shown as text and never interpreted by the browser.

#### Scenario: Markup in title
- **WHEN** an article title is `<script>alert(1)</script>`
- **THEN** the pages contain `&lt;script&gt;alert(1)&lt;/script&gt;` and no `<script>` element

### Requirement: Site is self-contained and portable
Publishing SHALL write `style.css`, and every page SHALL use only relative links to other pages and to the stylesheet, declare its language as `pt-BR`, and include no scripts, so the site works when opened from disk and from any static host.

#### Scenario: Pages use relative links
- **WHEN** a site is published
- **THEN** `style.css` exists and every page references it with a relative path
- **AND** no page contains a `<script>` element or an absolute link to another page of the site

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
Publishing SHALL write the edition's files first, then `style.css` and the archive, then `editions.json`, and the root `index.html` last. When publishing fails midway, the root `index.html` and `editions.json` SHALL be left as they were.

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
