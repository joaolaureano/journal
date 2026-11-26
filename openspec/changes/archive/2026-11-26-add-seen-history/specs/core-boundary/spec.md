## ADDED Requirements

### Requirement: History contract
The core SHALL define a history contract: an operation that, given a date, returns the keys of the articles first published in an edition dated before it. An article's key SHALL be its URL normalized as for deduplication.

#### Scenario: Fake history satisfies the contract
- **WHEN** an in-memory object exposes that operation
- **THEN** it is recognized as a history
