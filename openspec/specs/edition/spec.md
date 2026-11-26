# edition Specification

## Purpose

Define a edição diária do journal: a data e os artigos publicados para ela.

## Requirements

### Requirement: Edition groups one day's articles
The domain SHALL define an edition holding a calendar date and the articles published for it, in display order. An edition MAY have no articles.

#### Scenario: Edition of a day
- **WHEN** an edition is created for 2026-11-26 with two articles
- **THEN** it exposes that date and the two articles in the given order
