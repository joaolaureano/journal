## MODIFIED Requirements

### Requirement: Lambda handler
`journal.aws_lambda.handler` SHALL run the same build as `journal build`, with the configuration from `JOURNAL_CONFIG` (default: `journal.toml` packaged next to the `journal` package), publishing to the bucket in `JOURNAL_BUCKET` (and `JOURNAL_PREFIX`) when set. It SHALL return the edition date and counts, log source failures, and raise when the build or publishing fails, except when the event asks for a collection.

#### Scenario: Scheduled run
- **WHEN** the handler runs with `JOURNAL_BUCKET` set and sources that respond
- **THEN** the edition is published to that bucket and the handler returns its date and article count

### Requirement: Daily schedule and hosting
The deployment (OpenTofu configuration in `deploy/`) SHALL create a private, versioned bucket served only through CloudFront, a function running the handler, and a schedule invoking it Monday to Saturday at 08:00 in `America/Sao_Paulo`, never on Sunday, both configurable. It SHALL also create a second schedule invoking the function with the event `{"action": "collect"}` every hour at minute 30, every day, configurable, and SHALL expire noncurrent versions of objects under `pool/` after 1 day.

#### Scenario: Default schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function runs Monday to Saturday at 08:00 São Paulo time and not on Sunday

#### Scenario: Default collection schedule
- **WHEN** the template is deployed with default parameters
- **THEN** the function collects at minute 30 of every hour, including Sundays, and never at the same minute as the edition

## ADDED Requirements

### Requirement: Collection through the Lambda handler
When the event is an object whose `action` is `"collect"`, the handler SHALL run the same collection as `journal collect` on the same storage, without reading the summarizer key. It SHALL return the number of articles collected and the source failures, and raise when the collection fails.

#### Scenario: Scheduled collection
- **WHEN** the handler runs with the event `{"action": "collect"}` and `JOURNAL_BUCKET` set
- **THEN** the pool entries in that bucket are updated, no edition is published and the SSM key is not read
