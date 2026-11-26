# Spec Delta

## MODIFIED Requirements

### Requirement: S3 storage
The `s3` storage SHALL implement the static site storage contract on keys under an optional prefix of a bucket. Writes SHALL set `Content-Type` from the file extension (`charset=utf-8` for text and JSON) and `Cache-Control` of 5 minutes for `index.html`, `artigos.html`, `edicoes/index.html`, `editions.json` and `seen.json`, and of one year, immutable, for every other key. A missing key SHALL read as absent; any other failure SHALL raise the publish error naming the S3 location.

#### Scenario: Round trip with prefix
- **WHEN** `a.html` is written to bucket `b` with prefix `site`
- **THEN** the object `site/a.html` exists in `b` and reads back the same bytes

#### Scenario: Access denied
- **WHEN** S3 answers a write with `AccessDenied`
- **THEN** the storage raises the publish error mentioning `s3://<bucket>/<key>`
