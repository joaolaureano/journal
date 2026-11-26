## ADDED Requirements

### Requirement: Bare articles link to their source
In an edition's list, an article with neither summary nor image SHALL have its title link straight to its source URL instead of its article page, which is still written.

#### Scenario: Article without summary or image
- **WHEN** an edition holds an article with an empty summary and no image
- **THEN** its title in the list links to the article's source URL
- **AND** its article page still exists
