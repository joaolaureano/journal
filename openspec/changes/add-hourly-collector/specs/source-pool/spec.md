## ADDED Requirements

### Requirement: Pooled reading of a source
When the pool is configured, every fetch of a source SHALL return the articles in its feed together with the articles that earlier fetches of the same source stored and that were published within the last `hours` hours, one per article key, the feed's version winning over the stored one. The fetch SHALL then store that combined set for the source in the publisher's storage, under `pool/`, without articles older than the window and with at most the 1000 newest.

#### Scenario: Item that left the feed
- **WHEN** an hourly fetch stored an item at 03:30 and the feed no longer lists it at 08:00, 4.5 hours later, with `hours = 48`
- **THEN** the 08:00 build still receives that item

#### Scenario: Item outside the window
- **WHEN** a stored item was published 50 hours before the fetch and `hours = 48`
- **THEN** the fetch does not return it and it is no longer stored

#### Scenario: Same item in feed and pool
- **WHEN** the feed and the pool both hold an item with the same key and the feed's title changed
- **THEN** the fetch returns it once, with the feed's title

### Requirement: Pool failures stay with their source
A missing or unreadable pool entry SHALL count as empty, so the fetch returns the feed's articles and replaces the entry. When the feed fails, the fetch SHALL raise the source error as without a pool and SHALL leave the stored entry unchanged. When the storage cannot save the entry, the fetch SHALL raise a source error naming the source.

#### Scenario: Corrupt pool entry
- **WHEN** a source's pool entry is not valid JSON
- **THEN** the fetch returns the feed's articles and stores a valid entry with them

#### Scenario: Feed down during a collection
- **WHEN** a feed does not answer during an hourly collection
- **THEN** that source is reported as failed and its stored items are still available to the next fetch

### Requirement: Collection without publishing
The `journal collect` command SHALL fetch every configured source through the pool, with the configuration given by `--config` (default `journal.toml`), and SHALL NOT publish, update the edition history or call the summarizer. It SHALL print each source failure and the number of items stored, and exit with a non-zero status when the configuration has no `[pool]` table, cannot be loaded, or no source fetched successfully.

#### Scenario: Hourly collection
- **WHEN** `journal collect` runs with a `[pool]` table and sources that respond
- **THEN** each source's pool entry is updated and no page, edition list or AI text is written

#### Scenario: Collection without a pool
- **WHEN** `journal collect` runs with a configuration that has no `[pool]` table
- **THEN** it exits with a non-zero status saying the pool is not configured, and fetches nothing
