# journal-build Specification

## Purpose

Define como um build do journal reúne artigos de todas as fontes configuradas numa única lista ordenada e sem duplicatas e a entrega ao publicador, inclusive pela linha de comando.

## Requirements

### Requirement: Build gathers articles from every source
A build SHALL fetch from every configured source, in configured order, and combine their articles.

#### Scenario: Two sources
- **WHEN** a build runs with two sources returning two articles each, all with distinct URLs
- **THEN** the publisher receives all four articles

### Requirement: Failing source does not stop the build
A source that raises the source error SHALL be reported in the build result while the articles from the other sources are still published.

#### Scenario: One of two sources fails
- **WHEN** one source raises the source error and the other returns articles
- **THEN** the publisher receives the articles from the working source
- **AND** the build result lists the failure

### Requirement: Build without any successful source does not publish
When no source fetches successfully, including when no source is configured, the build SHALL fail and the publisher SHALL NOT be called, so a previously published site is left untouched.

#### Scenario: All sources fail
- **WHEN** every source raises the source error
- **THEN** the build fails
- **AND** the publisher is not called

#### Scenario: Successful source with no articles
- **WHEN** the only source succeeds and returns no articles
- **THEN** the build succeeds and the publisher receives an empty list

### Requirement: Articles are deduplicated by URL
Articles with the same URL SHALL be published once, keeping the first occurrence in source order and, within a source, in the order the source returned them.

#### Scenario: Same URL in two sources
- **WHEN** two sources return an article with the same URL but different titles
- **THEN** the publisher receives that URL once, with the title from the first source

### Requirement: Articles are ordered newest first
Published articles SHALL be ordered by publication timestamp, newest first, with ties ordered by URL ascending so repeated builds produce the same order.

#### Scenario: Mixed dates
- **WHEN** sources return articles published at 09:00, 11:00 and 10:00
- **THEN** the publisher receives them in the order 11:00, 10:00, 09:00

#### Scenario: Same timestamp
- **WHEN** two articles share a publication timestamp
- **THEN** the one with the lexicographically smaller URL comes first

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

### Requirement: Articles can be filtered by keywords
When a keyword filter is configured, the build SHALL publish only articles whose title or summary contains at least one `include` term, when `include` terms are given, and none of the `exclude` terms. Terms SHALL match whole words or phrases, ignoring case and accents. When the filter leaves no articles, the build SHALL still succeed and publish an empty list.

#### Scenario: Include term
- **WHEN** the filter includes `selic` and articles are titled "Copom mantém a Selic" and "Time vence clássico"
- **THEN** the publisher receives only "Copom mantém a Selic"

#### Scenario: Case and accents are ignored
- **WHEN** the filter includes `inflacao` and an article summary mentions "INFLAÇÃO"
- **THEN** the article is published

#### Scenario: Whole words only
- **WHEN** the filter includes `juros` and an article is titled "Conjuros antigos"
- **THEN** the article is not published

#### Scenario: Exclude wins over include
- **WHEN** the filter includes `banco` and excludes `futebol`, and an article is titled "Banco patrocina time de futebol"
- **THEN** the article is not published

#### Scenario: Filter removes everything
- **WHEN** sources return articles and none matches the filter
- **THEN** the build succeeds and the publisher receives an empty list

### Requirement: Number of published articles can be capped
When a maximum number of articles is configured, the build SHALL publish at most that many articles, keeping the newest after filtering and ordering.

#### Scenario: Cap keeps the newest
- **WHEN** the maximum is 2 and three articles published at 09:00, 10:00 and 11:00 pass the filter
- **THEN** the publisher receives the 11:00 and 10:00 articles
