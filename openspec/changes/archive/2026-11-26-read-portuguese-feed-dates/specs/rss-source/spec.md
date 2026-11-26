# Spec Delta

## ADDED Requirements

### Requirement: Portuguese feed dates are read
When feedparser cannot parse an entry's published or updated date, the RSS source SHALL read it as an RFC 822 date whose weekday and month may be Portuguese abbreviations (`Seg`, `Ter`, `Qua`, `Qui`, `Sex`, `Sáb`, `Dom`; `Fev`, `Abr`, `Mai`, `Ago`, `Set`, `Out`, `Dez` besides the English ones). An entry whose date still cannot be read SHALL be skipped as having no date.

#### Scenario: UOL date
- **WHEN** an entry's date is `Qui, 26 Nov 2026 10:08:44 -0300`
- **THEN** the article's publication timestamp is 2026-11-26 13:08:44 UTC

#### Scenario: Portuguese month
- **WHEN** an entry's date is `Sáb, 05 Dez 2026 08:00:00 -0300`
- **THEN** the article's publication timestamp is 2026-12-05 11:00:00 UTC

#### Scenario: Unreadable date
- **WHEN** an entry's date is `ontem à tarde`
- **THEN** the entry is skipped
