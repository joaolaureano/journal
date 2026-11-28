## ADDED Requirements

### Requirement: Front page layout
The stories on the front page SHALL be laid out as a newspaper: the first as the lead, wide, with its first item's image large and credited when the feed has one; the next four as a row of teasers; the rest as compact notes. The news list SHALL follow as one band per section, items in a grid. Without an image, an entry SHALL show text in its place. On narrow screens everything SHALL stack in one column.

#### Scenario: Lead story with image
- **WHEN** the first story's first item has an image with a credit
- **THEN** the front page shows that image in the lead entry with the credit

#### Scenario: Lead story without image
- **WHEN** the first story's first item has no image
- **THEN** the lead entry has no image and no empty figure

## MODIFIED Requirements

### Requirement: Story entry on the front page
Each story on the front page SHALL show its section, the number of distinct sources (`1 fonte`, `3 fontes`) and one link per item to its page, labelled with the item's source. A story with text SHALL show its written title linking to its story page, the label `Texto por IA`, its first paragraph and, when it has divergences, a `divergência` badge. A story without text SHALL show its first item's title linking to that item's page and its first item's summary.

#### Scenario: Story with three sources
- **WHEN** an edition's first story has items from g1 política, CNN Brasil política and JOTA
- **THEN** the front page shows it first, with `3 fontes` and links labelled g1 política, CNN Brasil política and JOTA

#### Scenario: Written story with a divergence
- **WHEN** a story has a written text with one divergence
- **THEN** its front-page entry shows the written title, `Texto por IA`, the first paragraph and the `divergência` badge, and links to the story page

### Requirement: Menu stays put while the content scrolls
The menu SHALL stay fixed at the left of the viewport with its own scrolling, closed by default on every screen, and a menu button SHALL toggle it without scripts.

#### Scenario: Narrow screen
- **WHEN** a page is opened on a narrow screen
- **THEN** the menu is hidden until the menu button is activated

#### Scenario: Wide screen
- **WHEN** a page is opened on a wide screen
- **THEN** the menu is hidden until the menu button is activated
