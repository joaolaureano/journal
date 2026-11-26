## MODIFIED Requirements

### Requirement: Publisher contract
The core SHALL define a publisher contract: an operation that receives an edition and returns nothing. Any object offering that operation SHALL be usable as a publisher.

#### Scenario: Fake publisher satisfies the contract
- **WHEN** an in-memory object exposing the publish operation receives an edition
- **THEN** it is recognized as a publisher
