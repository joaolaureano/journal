# Spec Delta

## MODIFIED Requirements

### Requirement: Build command
The `journal build` command SHALL run a build with one RSS feed given by `--feed` and `--name`, publishing to the directory given by `--out` (default `dist`), print how many articles were published and any source failures, and exit with status 0 on success and non-zero when the build or publishing fails.

#### Scenario: Successful build from the command line
- **WHEN** `journal build --feed <feed URL> --name Example --out <dir>` runs against a valid feed
- **THEN** the output directory contains the published site
- **AND** the command prints the number of published articles and exits with status 0

#### Scenario: Failing feed from the command line
- **WHEN** `journal build` runs with a feed that cannot be fetched
- **THEN** the command prints the failure, exits with a non-zero status and does not write the output directory

#### Scenario: Publishing fails from the command line
- **WHEN** `journal build` fetches articles but the publisher raises the publish error
- **THEN** the command prints the failure and exits with a non-zero status
