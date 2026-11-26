## ADDED Requirements

### Requirement: Publication history
The static site SHALL act as the journal's history through `seen.json` at the root: a JSON object mapping each published article's key to the date of the first edition that published it. Publishing SHALL add the edition's articles, keeping an existing date, SHALL drop entries more than 90 days older than the edition date, and SHALL write `seen.json` before `editions.json`. A `seen.json` that is not a JSON object SHALL make the history and publishing fail with the publish error.

#### Scenario: Earlier days only
- **WHEN** article A was published on 2026-11-25 and article B on 2026-11-26
- **THEN** the history for 2026-11-26 holds only A's key

#### Scenario: Revision keeps the first date
- **WHEN** article A was published on 2026-11-25 and again in an edition of 2026-11-26
- **THEN** `seen.json` keeps 2026-11-25 for A

#### Scenario: Retention
- **WHEN** an article was published 117 days before the latest edition
- **THEN** it is no longer in the history
