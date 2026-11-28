## ADDED Requirements

### Requirement: Pages have an icon
Every page SHALL declare an icon for browser tabs, embedded in the page as an SVG data URL, so no extra file or request is needed.

#### Scenario: Icon on every page
- **WHEN** a site is published
- **THEN** every page has a `<link rel="icon">` with an SVG data URL
