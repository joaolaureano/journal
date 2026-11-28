# edition Specification

## Purpose

Define a edição diária do journal: a data e os artigos publicados para ela.

## Requirements

### Requirement: Edition groups one day's articles
The domain SHALL define an edition holding a calendar date and the articles published for it, in display order, and the timezone that decided the date (UTC by default). An edition MAY have no articles.

#### Scenario: Edition of a day
- **WHEN** an edition is created for 2026-11-26 with two articles
- **THEN** it exposes that date and the two articles in the given order

### Requirement: Edition stories
An edition SHALL carry the stories chosen for it, in display order, empty by default. Each story SHALL hold at least one article, its section, if any, and an id derived from its articles' keys, so the same items always give the same id.

#### Scenario: Edition without grouper
- **WHEN** an edition is built without a grouper
- **THEN** it has no stories
