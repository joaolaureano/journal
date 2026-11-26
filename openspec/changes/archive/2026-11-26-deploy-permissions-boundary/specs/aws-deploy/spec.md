## ADDED Requirements

### Requirement: Optional permissions boundary
The deployment SHALL accept an optional permissions boundary ARN and, when given, attach it to every IAM role it creates; every resource name SHALL start with the configured name prefix and every role SHALL carry the `Project` tag with that prefix, so a tag-based boundary can scope the roles to their own resources.

#### Scenario: Boundary given
- **WHEN** the deployment runs with `permissions_boundary` set to a policy ARN
- **THEN** the function role and the scheduler role are created with that policy as their permissions boundary

#### Scenario: No boundary
- **WHEN** the deployment runs without `permissions_boundary`
- **THEN** the roles are created without a permissions boundary
