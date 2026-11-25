# Spec Delta

## MODIFIED Requirements

### Requirement: Build command
The `journal build` command SHALL run a build with the sources and publisher declared in the configuration file given by `--config` (default `journal.toml`), print how many articles were published and any source failures, and exit with status 0 on success and non-zero when the configuration is invalid, the build fails or publishing fails.

#### Scenario: Successful build from the command line
- **WHEN** `journal build --config <file>` runs with a configuration declaring two valid RSS feeds
- **THEN** the configured output directory contains the published site with articles from both feeds
- **AND** the command prints the number of published articles and exits with status 0

#### Scenario: Failing feed from the command line
- **WHEN** `journal build` runs with a configuration whose only feed cannot be fetched
- **THEN** the command prints the failure, exits with a non-zero status and does not write the output directory

#### Scenario: Publishing fails from the command line
- **WHEN** `journal build` fetches articles but the publisher raises the publish error
- **THEN** the command prints the failure and exits with a non-zero status

#### Scenario: Invalid configuration from the command line
- **WHEN** `journal build` runs with a configuration file that is missing or invalid
- **THEN** the command prints what is wrong, exits with a non-zero status and does not write the output directory
