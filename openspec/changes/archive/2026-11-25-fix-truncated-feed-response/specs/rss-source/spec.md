## MODIFIED Requirements

### Requirement: Feed failures raise a source error
Fetching SHALL raise the core source error, naming the feed location, when the feed cannot be retrieved, does not answer within the configured timeout, its transfer is cut before the full response arrives, or its content is not a feed.

#### Scenario: Unreachable feed
- **WHEN** the feed location does not exist
- **THEN** fetching raises the source error

#### Scenario: Slow feed
- **WHEN** the feed server accepts the connection but does not answer within the timeout
- **THEN** fetching raises the source error instead of waiting indefinitely

#### Scenario: Truncated response
- **WHEN** the feed server announces a response length and closes the connection before sending all of it
- **THEN** fetching raises the source error

#### Scenario: Content is not a feed
- **WHEN** the feed location returns content that is not RSS or Atom
- **THEN** fetching raises the source error
