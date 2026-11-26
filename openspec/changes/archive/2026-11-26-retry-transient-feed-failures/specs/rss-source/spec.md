## ADDED Requirements

### Requirement: Transient feed failures are retried
Fetching SHALL retry a feed up to a configurable number of extra attempts (default 2), waiting a growing delay between them (default 1 s, then 2 s), when the failure is transient: a network error or timeout, a cut transfer, an HTTP status 5xx, 408 or 429, or content that is not a feed. Any other HTTP 4xx status SHALL fail at once. When every attempt fails, fetching SHALL raise the source error of the last attempt.

#### Scenario: Server error then success
- **WHEN** the feed server answers 503 and then the feed
- **THEN** fetching returns the feed's articles

#### Scenario: Not found is not retried
- **WHEN** the feed server answers 404
- **THEN** fetching raises the source error after a single request

#### Scenario: Persistent failure
- **WHEN** the feed server answers 500 to every request
- **THEN** fetching raises the source error after the initial attempt and every retry
