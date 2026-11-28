## ADDED Requirements

### Requirement: Stories on the front page
When an edition has stories, its `index.html` and the root `index.html` SHALL show them before the news list, under `Histórias do dia`, in the edition's order, with the news list following under `Todas as notícias`. Without stories, the page SHALL be as before.

#### Scenario: No stories
- **WHEN** an edition has no stories
- **THEN** its front page has no `Histórias do dia` block

### Requirement: Story entry on the front page
Each story on the front page SHALL show its first item's title linking to that item's page, its first item's summary, the number of distinct sources (`1 fonte`, `3 fontes`) and one link per item to its page, labelled with the item's source.

#### Scenario: Story with three sources
- **WHEN** an edition's first story has items from g1 política, CNN Brasil política and JOTA
- **THEN** the front page shows it first, with `3 fontes` and links labelled g1 política, CNN Brasil política and JOTA

### Requirement: Stories file
Publishing SHALL write `stories.json` in the edition folder: a JSON array, in display order, with one object per story holding its `id`, `section`, the `ids` of its items and their distinct `sources`.

#### Scenario: Stories listed
- **WHEN** an edition with two stories is published
- **THEN** its `stories.json` has two objects with the items' ids

### Requirement: Story items count as published
The history SHALL record every item of a published story as published on the edition's date, also when the item is not in the edition's news list.

#### Scenario: Item cut from the list
- **WHEN** a story item did not fit the per-section limit of the news list
- **THEN** `seen.json` still records it, and later editions drop it
