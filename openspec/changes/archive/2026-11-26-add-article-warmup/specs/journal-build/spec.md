## ADDED Requirements

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
