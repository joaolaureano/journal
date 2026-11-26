## MODIFIED Requirements

### Requirement: Daily schedule and hosting
The deployment (OpenTofu configuration in `deploy/`) SHALL create a private, versioned bucket served only through CloudFront, a function running the handler, and a schedule invoking it daily at 08:00 in `America/Sao_Paulo`, both configurable.

#### Scenario: Default schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function runs every day at 08:00 São Paulo time
