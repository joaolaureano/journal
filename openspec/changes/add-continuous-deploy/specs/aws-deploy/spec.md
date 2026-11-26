## ADDED Requirements

### Requirement: Continuous deployment of the function code
On every push and pull request, the repository workflow SHALL run the linter and the test suite. On a push to `main` that passes them, and only when the repository variable `AWS_DEPLOY_ROLE_ARN` is set, it SHALL publish the package built by `deploy/build.sh` as the function's code, assuming that role through OIDC in the `production` environment.

#### Scenario: Push to main
- **WHEN** a commit that passes the tests is pushed to `main` and the role variable is set
- **THEN** the function runs the code and `journal.toml` of that commit

#### Scenario: Fork without the role
- **WHEN** the workflow runs in a repository without `AWS_DEPLOY_ROLE_ARN`
- **THEN** the tests run and the publication is skipped

#### Scenario: Pull request
- **WHEN** a pull request is opened
- **THEN** the tests run and nothing is published

### Requirement: Optional deploy role for CI
The deployment SHALL create the CI role only when a GitHub subject prefix is given, trusting only that repository's `production` environment and allowing only to update and read the function's code.

#### Scenario: No subject prefix
- **WHEN** the deployment runs without `github_subject_prefix`
- **THEN** no CI role is created
