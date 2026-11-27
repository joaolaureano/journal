## ADDED Requirements

### Requirement: Articles can be filtered by link domain
When excluded domains are configured, the build SHALL drop every article whose link host is one of those domains or a subdomain of one, ignoring case. A host that only ends with the same letters SHALL NOT match.

#### Scenario: Paywalled outlet inside another feed
- **WHEN** `folha.uol.com.br` is excluded and a feed returns links on `www1.folha.uol.com.br` and `noticias.uol.com.br`
- **THEN** only the `noticias.uol.com.br` article is published

#### Scenario: Similar name is not a subdomain
- **WHEN** `folha.com.br` is excluded and an article links to `minhafolha.com.br`
- **THEN** that article is published
