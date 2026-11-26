## MODIFIED Requirements

### Requirement: Failing source does not stop the build
A source that raises the source error, or any other exception, SHALL be reported in the build result as a source error while the articles from the other sources are still published.

#### Scenario: One of two sources fails
- **WHEN** one source raises the source error and the other returns articles
- **THEN** the publisher receives the articles from the working source
- **AND** the build result lists the failure

#### Scenario: Source raises an unexpected exception
- **WHEN** one source raises an exception that is not the source error and the other returns articles
- **THEN** the publisher receives the articles from the working source
- **AND** the build result lists a source error naming the failing source

### Requirement: Articles are deduplicated by URL
Articles whose URLs differ only in scheme (`http`/`https`), a leading `www.`, host case, a trailing slash, the fragment or tracking query parameters (`utm_*`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`) SHALL be published once, keeping the first occurrence in source order and, within a source, in the order the source returned them. The kept article SHALL keep its original URL.

#### Scenario: Same URL in two sources
- **WHEN** two sources return an article with the same URL but different titles
- **THEN** the publisher receives that URL once, with the title from the first source

#### Scenario: Same story with URL noise
- **WHEN** one source returns `https://example.com/news/1` and another returns `http://www.example.com/news/1/?utm_source=rss`
- **THEN** the publisher receives only the first one

#### Scenario: Meaningful query is kept
- **WHEN** a source returns `https://example.com/?p=1` and `https://example.com/?p=2`
- **THEN** the publisher receives both

## ADDED Requirements

### Requirement: Articles outside the time window are dropped
The build SHALL drop articles dated more than one day after the current time. When a maximum age in days is configured, it SHALL also drop articles published before the current time minus that many days.

#### Scenario: Stale article
- **WHEN** the maximum age is 2 days and articles are 1 and 3 days old
- **THEN** the publisher receives only the 1-day-old article

#### Scenario: Far-future article
- **WHEN** no filter is configured and articles are dated 3 hours and 2 days in the future
- **THEN** the publisher receives only the one dated 3 hours ahead
