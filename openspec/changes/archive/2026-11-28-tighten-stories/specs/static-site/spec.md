## MODIFIED Requirements

### Requirement: Story entry on the front page
Each story on the front page SHALL show its section, the number of distinct sources (`1 fonte`, `3 fontes`) and one link per distinct source, to that source's first item. A story with text SHALL show its written title linking to its story page, the label `Texto por IA`, its first paragraph and, when it has divergences, a `divergência` badge. A story without text SHALL show its first item's title, linking to its page, and summary.

#### Scenario: Story with three sources
- **WHEN** an edition's first story has items from g1 política, CNN Brasil política and JOTA
- **THEN** the front page shows it first, with `3 fontes` and links labelled g1 política, CNN Brasil política and JOTA

#### Scenario: Written story with a divergence
- **WHEN** a story has a written text with one divergence
- **THEN** its front-page entry shows the written title, `Texto por IA`, the first paragraph and the `divergência` badge, and links to the story page

#### Scenario: Several items from one source
- **WHEN** a story has two items from g1 política and one from JOTA
- **THEN** its entry links g1 política once and JOTA once
