# Spec Delta

## ADDED Requirements

### Requirement: Article list page
Publishing SHALL write `index.html` listing every article in the order received, each with its title linking to its article page, its source, its publication date and its summary. With no articles, the page SHALL say that there are no articles.

#### Scenario: Index lists articles in order
- **WHEN** two articles are published
- **THEN** `index.html` shows both titles in the order received
- **AND** each title links to `articles/<id>.html` of that article

#### Scenario: Empty site
- **WHEN** an empty list is published
- **THEN** `index.html` exists and states that there are no articles

### Requirement: Article page
Publishing SHALL write `articles/<id>.html` for every article, showing its title, source, publication date and summary, a link to the original URL and a link back to the list page.

#### Scenario: Article page content
- **WHEN** an article is published
- **THEN** `articles/<id>.html` shows its title, source, date and summary
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

### Requirement: Site is replaced as a whole
Each publish SHALL leave the output directory holding exactly the new site, with no pages from earlier publishes, and the previous site SHALL stay in place until the new one is completely written.

#### Scenario: Article removed between publishes
- **WHEN** a site with articles A and B is published and then a site with only A
- **THEN** the output directory has no page for B

#### Scenario: Publish fails midway
- **WHEN** writing the new site fails before it is complete
- **THEN** the previously published site is still in the output directory, unchanged

### Requirement: Unrelated directories are never replaced
Publishing SHALL raise the publish error and leave the directory untouched when the output directory exists, is not empty and does not contain a previously published site.

#### Scenario: Output points at a directory with other files
- **WHEN** publishing to an existing directory that holds files but no `articles.json`
- **THEN** publishing raises the publish error
- **AND** the directory and its files are unchanged

#### Scenario: Output is an empty directory
- **WHEN** publishing to an existing empty directory
- **THEN** the site is published there
