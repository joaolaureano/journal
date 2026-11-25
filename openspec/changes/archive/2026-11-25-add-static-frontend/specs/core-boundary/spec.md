# Spec Delta

## ADDED Requirements

### Requirement: Publish failures are reported as a publish error
The core SHALL define a publish error type. A publisher that cannot publish SHALL raise that error, so callers can handle publishing failures without knowing which adapter produced them.

#### Scenario: Caller handles failure without knowing the adapter
- **WHEN** a publisher fails and raises the publish error
- **THEN** a caller that only knows the core contracts can catch it as the publish error
