## ADDED Requirements

### Requirement: Comments-only summary is empty
A summary whose plain text is only the word "Comments" (any case), as aggregators such as Hacker News and Lobsters send, SHALL yield an empty summary.

#### Scenario: Aggregator entry
- **WHEN** an entry's summary is `<a href="https://news.example/item?id=1">Comments</a>`
- **THEN** the article summary is empty
