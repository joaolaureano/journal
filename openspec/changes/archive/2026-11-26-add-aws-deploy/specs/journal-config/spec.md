## ADDED Requirements

### Requirement: Built-in S3 storage type
The `s3` storage type SHALL take a required `bucket` (string) and an optional `prefix` (string, default empty). It needs boto3 installed (`journal[aws]`).

#### Scenario: S3 storage from configuration
- **WHEN** the publisher declares `storage = { type = "s3", bucket = "meu-jornal" }`
- **THEN** the static site is written to the bucket `meu-jornal`
