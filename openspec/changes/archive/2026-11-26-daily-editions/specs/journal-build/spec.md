## ADDED Requirements

### Requirement: Build publishes the edition of the day
A build SHALL hand the publisher one edition holding the published articles, dated with the current date in the configured timezone (UTC when none is given).

#### Scenario: Late evening in São Paulo
- **WHEN** a build runs at 2026-11-27 02:00 UTC with timezone `America/Sao_Paulo`
- **THEN** the publisher receives an edition dated 2026-11-26
