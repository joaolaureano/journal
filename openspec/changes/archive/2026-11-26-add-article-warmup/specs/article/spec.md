## ADDED Requirements

### Requirement: Article may carry an AI warm-up
An article SHALL accept an optional `warmup`, absent by default: a short plain-text paragraph written by a language model from the article's own text, never markup.

#### Scenario: No warm-up by default
- **WHEN** an article is created without a warm-up
- **THEN** its warm-up is absent

#### Scenario: Warm-up kept as given
- **WHEN** an article is created with warm-up `Um resumo curto.`
- **THEN** its warm-up is `Um resumo curto.`
