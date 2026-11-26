## ADDED Requirements

### Requirement: S3 storage
The `s3` storage SHALL implement the static site storage contract on keys under an optional prefix of a bucket. Writes SHALL set `Content-Type` from the file extension (with `charset=utf-8` for text and JSON) and `Cache-Control` of 5 minutes for `index.html`, `edicoes/index.html`, `editions.json` and `seen.json`, and of one year, immutable, for every other key. A missing key SHALL read as absent; any other failure SHALL raise the publish error naming the S3 location.

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
The deployment template SHALL create a private, versioned bucket served only through CloudFront, a function running the handler, and a schedule invoking it daily at 08:00 in `America/Sao_Paulo`, both configurable.

#### Scenario: Default schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function runs every day at 08:00 São Paulo time
