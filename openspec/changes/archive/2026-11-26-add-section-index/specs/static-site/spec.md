## ADDED Requirements

### Requirement: Section index
When an edition list page shows section headings, each heading SHALL carry an `id` made from its name (lowercase, accents removed, words joined by hyphens), and the page SHALL show, right below the edition label, one link per section in page order pointing to that heading on the same page. A page without section headings SHALL show no index.

#### Scenario: Index of an edition with sections
- **WHEN** an edition holds articles of "Ciência" and "Brasil e mundo", in that order
- **THEN** below the edition label the page links to `#ciencia` and then `#brasil-e-mundo`, and the headings carry those ids

#### Scenario: No sections
- **WHEN** no article of the edition has a section
- **THEN** the page shows no section index
