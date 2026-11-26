## MODIFIED Requirements

### Requirement: Daily schedule and hosting
The deployment (OpenTofu configuration in `deploy/`) SHALL create a private, versioned bucket served only through CloudFront, a function running the handler, and a schedule invoking it Monday to Saturday at 08:00 in `America/Sao_Paulo`, never on Sunday, both configurable.

#### Scenario: Default schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function runs Monday to Saturday at 08:00 São Paulo time and not on Sunday
