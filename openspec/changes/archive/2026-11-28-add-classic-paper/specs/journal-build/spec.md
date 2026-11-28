## ADDED Requirements

### Requirement: Evergreen articles skip the age limit
The build SHALL NOT drop an evergreen article for being older than the configured maximum age. Evergreen articles dated more than one day in the future SHALL still be dropped, and the edition history SHALL still drop an evergreen article published in an earlier edition.

#### Scenario: Classic paper in today's edition
- **WHEN** `max_age_days = 2` and a source returns an evergreen article published in 2017
- **THEN** the article is published in today's edition

#### Scenario: Already shown
- **WHEN** an evergreen article was published in an earlier edition
- **THEN** the build drops it like any other article
