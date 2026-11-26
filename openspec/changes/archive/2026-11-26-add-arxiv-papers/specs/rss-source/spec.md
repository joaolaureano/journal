# Spec Delta

## ADDED Requirements

### Requirement: arXiv announcements are cleaned
The RSS source SHALL remove a leading `arXiv:<id> Announce Type: <type>` line and `Abstract:` label from the entry's text before building the summary and the body, and SHALL skip entries whose arXiv announce type is `replace` or `replace-cross`, which re-announce papers already published.

#### Scenario: New paper
- **WHEN** an entry's summary is `arXiv:2611.33159v1 Announce Type: new \nAbstract: Normal Distributions Transform scan matching…`
- **THEN** the article summary starts with `Normal Distributions Transform`

#### Scenario: Replacement skipped
- **WHEN** an entry's arXiv announce type is `replace`
- **THEN** the source returns no article for it
