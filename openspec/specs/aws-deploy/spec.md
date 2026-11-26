# aws-deploy Specification

## Purpose

Define como o journal roda na AWS: armazenamento S3, handler da Lambda e infraestrutura do deploy diário.

## Requirements

### Requirement: S3 storage
The `s3` storage SHALL implement the static site storage contract on keys under an optional prefix of a bucket. Writes SHALL set `Content-Type` from the file extension (`charset=utf-8` for text and JSON) and `Cache-Control` of 5 minutes for `index.html`, `artigos.html`, `edicoes/index.html`, `editions.json` and `seen.json`, and of one year, immutable, for every other key. A missing key SHALL read as absent; any other failure SHALL raise the publish error naming the S3 location.

#### Scenario: Round trip with prefix
- **WHEN** `a.html` is written to bucket `b` with prefix `site`
- **THEN** the object `site/a.html` exists in `b` and reads back the same bytes

#### Scenario: Access denied
- **WHEN** S3 answers a write with `AccessDenied`
- **THEN** the storage raises the publish error mentioning `s3://<bucket>/<key>`

### Requirement: Lambda handler
`journal.aws_lambda.handler` SHALL run the same build as `journal build`, with the configuration from `JOURNAL_CONFIG` (default: `journal.toml` packaged next to the `journal` package), publishing to the bucket in `JOURNAL_BUCKET` (and `JOURNAL_PREFIX`) when set. It SHALL return the edition date and counts, log source failures, and raise when the build or publishing fails.

#### Scenario: Scheduled run
- **WHEN** the handler runs with `JOURNAL_BUCKET` set and sources that respond
- **THEN** the edition is published to that bucket and the handler returns its date and article count

### Requirement: Daily schedule and hosting
The deployment (OpenTofu configuration in `deploy/`) SHALL create a private, versioned bucket served only through CloudFront, a function running the handler, and a schedule invoking it daily at 08:00 in `America/Sao_Paulo`, both configurable.

#### Scenario: Default schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function runs every day at 08:00 São Paulo time

### Requirement: Optional permissions boundary
The deployment SHALL accept an optional permissions boundary ARN and, when given, attach it to every IAM role it creates; every resource name SHALL start with the configured name prefix and every role SHALL carry the `Project` tag with that prefix, so a tag-based boundary can scope the roles to their own resources.

#### Scenario: Boundary given
- **WHEN** the deployment runs with `permissions_boundary` set to a policy ARN
- **THEN** the function role and the scheduler role are created with that policy as their permissions boundary

#### Scenario: No boundary
- **WHEN** the deployment runs without `permissions_boundary`
- **THEN** the roles are created without a permissions boundary

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
