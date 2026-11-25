# Spec Delta

## Purpose

Define como um build do journal reúne artigos de todas as fontes configuradas numa única lista ordenada e sem duplicatas e a entrega ao publicador, inclusive pela linha de comando.

## ADDED Requirements

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
The `journal build` command SHALL run a build with one RSS feed given by `--feed` and `--name`, publishing to the directory given by `--out` (default `dist`), print how many articles were published and any source failures, and exit with status 0 on success and non-zero when the build fails.

#### Scenario: Successful build from the command line
- **WHEN** `journal build --feed <feed URL> --name Example --out <dir>` runs against a valid feed
- **THEN** the output directory contains the published site
- **AND** the command prints the number of published articles and exits with status 0

#### Scenario: Failing feed from the command line
- **WHEN** `journal build` runs with a feed that cannot be fetched
- **THEN** the command prints the failure, exits with a non-zero status and does not write the output directory
