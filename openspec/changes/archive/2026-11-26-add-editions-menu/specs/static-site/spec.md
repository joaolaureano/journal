## ADDED Requirements

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
