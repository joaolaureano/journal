## REMOVED Requirements

### Requirement: Index is replaced atomically
**Reason**: There is no single site index to replace anymore; each edition has its own `articles.json`, written once.
**Migration**: Read `editions.json` and then `<path>articles.json` of the edition wanted.

### Requirement: Site is replaced as a whole
**Reason**: Editions accumulate; earlier editions must be kept.
**Migration**: See "Editions are never overwritten" and "Publish order keeps the site consistent".

## MODIFIED Requirements

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

### Requirement: Unrelated directories are never replaced
Publishing to local storage SHALL raise the publish error and leave the directory untouched when the output directory exists, is not empty and holds neither `editions.json` nor `articles.json` (a site from before editions). Storage keys SHALL never resolve outside the output directory.

#### Scenario: Output points at a directory with other files
- **WHEN** publishing to an existing directory that holds files but no `editions.json` or `articles.json`
- **THEN** publishing raises the publish error
- **AND** the directory and its files are unchanged

#### Scenario: Output is an empty directory
- **WHEN** publishing to an existing empty directory
- **THEN** the edition is published there

## ADDED Requirements

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
