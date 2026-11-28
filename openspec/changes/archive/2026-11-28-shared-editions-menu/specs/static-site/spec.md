## MODIFIED Requirements

### Requirement: Editions menu
Every page SHALL show the editions menu from one shared `menu.html` at the site root, rewritten on every publish, so pages of earlier editions also list later ones. It SHALL list the 30 most recent editions, newest first, each as `DD/MM/YYYY` (plus ` · <revision>` after the first) linking to its folder, link to the front page and the archive, open links in the whole window, and mark the page's own edition.

#### Scenario: Menu on the front page
- **WHEN** editions of 2026-11-25 and 2026-11-26 are published
- **THEN** the menu lists `26/11/2026` then `25/11/2026`, and the front page marks `26/11/2026` as current

#### Scenario: Earlier edition sees later ones
- **WHEN** editions of 2026-11-25 and 2026-11-26 are published
- **THEN** the page of 2026-11-25 shows the shared menu, which lists `26/11/2026`, with `25/11/2026` marked

#### Scenario: Many editions
- **WHEN** 31 editions have been published
- **THEN** the menu lists the 30 most recent and links to the archive
