## ADDED Requirements

### Requirement: Edition stories
An edition SHALL carry the stories chosen for it, in display order, empty by default. Each story SHALL hold at least one article, its section, if any, and an id derived from its articles' keys, so the same items always give the same id.

#### Scenario: Edition without grouper
- **WHEN** an edition is built without a grouper
- **THEN** it has no stories
