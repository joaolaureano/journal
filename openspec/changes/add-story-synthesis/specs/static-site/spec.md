## MODIFIED Requirements

### Requirement: Story entry on the front page
Each story on the front page SHALL show the number of distinct sources (`1 fonte`, `3 fontes`) and one link per item to its page, labelled with the item's source. A story with text SHALL show its written title linking to its story page, its first paragraph and, when it has divergences, a `divergência` badge. A story without text SHALL show its first item's title linking to that item's page and its first item's summary.

#### Scenario: Story with three sources
- **WHEN** an edition's first story has items from g1 política, CNN Brasil política and JOTA
- **THEN** the front page shows it first, with `3 fontes` and links labelled g1 política, CNN Brasil política and JOTA

#### Scenario: Written story with a divergence
- **WHEN** a story has a written text with one divergence
- **THEN** its front-page entry shows the written title, the first paragraph and the `divergência` badge, and links to the story page

### Requirement: Stories file
Publishing SHALL write `stories.json` in the edition folder: a JSON array, in display order, with one object per story holding its `id`, `section`, the `ids` of its items, their distinct `sources` and its `text`: null, or the title, the paragraphs with the ids that support them and the divergences.

#### Scenario: Stories listed
- **WHEN** an edition with two stories is published
- **THEN** its `stories.json` has two objects with the items' ids

## ADDED Requirements

### Requirement: Story page
Publishing SHALL write `historias/<id>.html` in the edition folder for every story with text. It SHALL show the written title, the label `Texto gerado por IA a partir de:` followed by a link to each item's page, each paragraph followed by the sources that support it, a `Divergências` block with each point and the version of each source when there are any, and a list of the sources with a link to each original that opens in a new tab. All text from the model SHALL be HTML-escaped.

#### Scenario: Story page with sources
- **WHEN** a story with text from g1 política and JOTA is published
- **THEN** its page credits both, shows each paragraph's sources and links to both originals

#### Scenario: Markup in the model's text
- **WHEN** a paragraph from the model contains `<script>`
- **THEN** the story page shows it as text
