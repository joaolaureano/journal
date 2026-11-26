# Spec Delta

## ADDED Requirements

### Requirement: Any source can declare its kind
Every source entry, whatever its type, MAY have a `kind`, `"noticia"` or `"artigo"`, which its articles carry; without it they are news. Any other value SHALL be rejected with a configuration error mentioning `kind`.

#### Scenario: Blog as article source
- **WHEN** an `rss` source declares `kind = "artigo"`
- **THEN** its articles have kind `artigo`

#### Scenario: Invalid kind
- **WHEN** a source declares `kind = "blog"`
- **THEN** loading fails with a configuration error naming `kind`
