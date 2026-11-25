# Spec Delta

## ADDED Requirements

### Requirement: Source failures are reported as a source error
The core SHALL define a source error type. A source that cannot deliver its articles SHALL raise that error, so callers can handle failures from any source without knowing which adapter produced them.

#### Scenario: Caller handles failure without knowing the adapter
- **WHEN** a source fails to fetch and raises the source error
- **THEN** a caller that only knows the core contracts can catch it as the source error
