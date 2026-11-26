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
A source that raises the source error, or any other exception, SHALL be reported in the build result as a source error while the articles from the other sources are still published.

#### Scenario: One of two sources fails
- **WHEN** one source raises the source error and the other returns articles
- **THEN** the publisher receives the articles from the working source
- **AND** the build result lists the failure

#### Scenario: Source raises an unexpected exception
- **WHEN** one source raises an exception that is not the source error and the other returns articles
- **THEN** the publisher receives the articles from the working source
- **AND** the build result lists a source error naming the failing source

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
Articles whose URLs differ only in scheme (`http`/`https`), a leading `www.`, host case, a trailing slash, the fragment or tracking query parameters (`utm_*`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`) SHALL be published once, keeping the first occurrence in source order and, within a source, in the order the source returned them. The kept article SHALL keep its original URL.

#### Scenario: Same URL in two sources
- **WHEN** two sources return an article with the same URL but different titles
- **THEN** the publisher receives that URL once, with the title from the first source

#### Scenario: Same story with URL noise
- **WHEN** one source returns `https://example.com/news/1` and another returns `http://www.example.com/news/1/?utm_source=rss`
- **THEN** the publisher receives only the first one

#### Scenario: Meaningful query is kept
- **WHEN** a source returns `https://example.com/?p=1` and `https://example.com/?p=2`
- **THEN** the publisher receives both

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

### Requirement: Articles outside the time window are dropped
The build SHALL drop articles dated more than one day after the current time. When a maximum age in days is configured, it SHALL also drop articles published before the current time minus that many days.

#### Scenario: Stale article
- **WHEN** the maximum age is 2 days and articles are 1 and 3 days old
- **THEN** the publisher receives only the 1-day-old article

#### Scenario: Far-future article
- **WHEN** no filter is configured and articles are dated 3 hours and 2 days in the future
- **THEN** the publisher receives only the one dated 3 hours ahead

### Requirement: Build publishes the edition of the day
A build SHALL hand the publisher one edition holding the published articles, dated with the current date in the configured timezone (UTC when none is given).

#### Scenario: Late evening in São Paulo
- **WHEN** a build runs at 2026-11-27 02:00 UTC with timezone `America/Sao_Paulo`
- **THEN** the publisher receives an edition dated 2026-11-26

### Requirement: Stories from earlier days are not repeated
When a history is given, the build SHALL drop every article whose key the history reports as published before the edition's date, before applying the time window, the keyword filter and the cap, and SHALL report how many it dropped. Editions of the same date SHALL NOT count, so a later revision of a day redoes the whole day.

#### Scenario: Article already published yesterday
- **WHEN** the history reports article A as published before today and a source returns A and B
- **THEN** the publisher receives only B
- **AND** the build result reports one article already published

#### Scenario: URL variant of a published article
- **WHEN** the history reports `https://a.com/x` and a source returns `http://www.a.com/x/?utm_source=rss`
- **THEN** that article is not published

### Requirement: Articles are grouped by section
The edition's articles SHALL be grouped by section, in the order in which each section's first source is configured, with articles without section last; inside a group they keep the newest-first order.

#### Scenario: Section order follows the configuration
- **WHEN** sources are configured as "Tecnologia", one without section, then "Ciência"
- **THEN** the edition lists the "Tecnologia" articles, then the "Ciência" ones, then those without section

### Requirement: Number of articles per section can be capped
When a maximum per section is configured, the build SHALL keep at most that many of the newest articles of each section and kind (articles without section count as one section; news and articles of a section are counted apart), before applying the overall cap.

#### Scenario: Busy section is capped
- **WHEN** the maximum per section is 2, section "Busy" has articles at 09:00, 10:00 and 11:00 and section "Calm" one at 08:00
- **THEN** the edition holds the "Busy" articles of 11:00 and 10:00 and the "Calm" one

#### Scenario: News do not push articles out
- **WHEN** the maximum per section is 2 and section "Ciência" has three news and one article
- **THEN** the edition holds the two newest news and the article of "Ciência"

### Requirement: Articles get an AI warm-up
When the build has a summarizer, it SHALL ask it for a warm-up for every selected item of kind `artigo`, after selection and before publishing, several at a time, and publish each item with the warm-up returned. News items SHALL never be sent to the summarizer.

#### Scenario: Article and news item
- **WHEN** the selection holds one article and one news item and the summarizer answers `Resumo.`
- **THEN** the published article has warm-up `Resumo.` and the news item has none
- **AND** the summarizer was asked only about the article

#### Scenario: No summarizer
- **WHEN** the build has no summarizer
- **THEN** the edition is published without warm-ups

### Requirement: Warm-up failures do not stop the build
A summarizer error or answer `None` SHALL leave that item without warm-up. Items not answered within `warmup_timeout` seconds (default 180) SHALL be published without warm-up. The edition SHALL be published either way, and the report SHALL count the warm-ups and list each distinct error message once.

#### Scenario: Summarizer fails
- **WHEN** the summarizer raises an error for one of two articles
- **THEN** both articles are published, only the other one with a warm-up
- **AND** the report lists the error

#### Scenario: Summarizer too slow
- **WHEN** the summarizer does not answer within the warm-up timeout
- **THEN** the edition is published without that warm-up and the report says the warm-up timed out
