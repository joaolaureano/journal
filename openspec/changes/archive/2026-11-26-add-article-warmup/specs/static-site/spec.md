## ADDED Requirements

### Requirement: AI warm-up is shown and labelled
An item with a warm-up SHALL show it, escaped, in place of its summary on `artigos.html`, preceded by `Resumo por IA`, and on its article page above the text, labelled `Resumo gerado por IA a partir de <source>`. Items without warm-up SHALL look as before.

#### Scenario: Article with warm-up
- **WHEN** an article with summary `Do feed.` and warm-up `Da IA.` is published
- **THEN** its item on `artigos.html` shows `Da IA.` marked `Resumo por IA` and not `Do feed.`
- **AND** its page shows `Da IA.` labelled as AI-generated from its source, before its text

#### Scenario: Markup in warm-up
- **WHEN** a warm-up is `<b>x</b>`
- **THEN** the pages show `&lt;b&gt;x&lt;/b&gt;` and no `<b>` element

## MODIFIED Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the edition folder: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source`, `published_at` (ISO 8601 with UTC offset), `image`, `image_caption`, `image_credit`, `section`, `kind` and `warmup`, each `null` when the article has none.

#### Scenario: Two articles published
- **WHEN** an edition with two articles is published
- **THEN** the edition's `articles.json` holds two objects, in the same order, with all twelve fields

#### Scenario: Article without image
- **WHEN** an article without image is published
- **THEN** its object in `articles.json` has `image`, `image_caption` and `image_credit` set to `null`

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped
