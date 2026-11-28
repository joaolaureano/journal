## ADDED Requirements

### Requirement: News grouped into stories
When the build has a grouper, it SHALL hand it every news item (kind `noticia`) that passed the time window, the filter and the history, before the per-section limit, and turn its answer into stories: each group of items becomes one story, and every item in no group becomes a story of its own. An item SHALL belong to at most one story. A story's section SHALL be the section most of its items have, ties going to the section configured first.

#### Scenario: Same fact, three outlets
- **WHEN** the grouper puts the g1, CNN Brasil and JOTA items about the same STF decision in one group
- **THEN** the edition has one story with those three items

#### Scenario: Item left alone
- **WHEN** an item is in no group
- **THEN** it becomes a story with that item only

### Requirement: Stories ranked by coverage
The build SHALL rank stories by the number of distinct sources among their items, most first, ties going to the story with the newest item. It SHALL keep at most `max_stories` stories, taking first the best-ranked story of each section that has one, in configured section order, and filling the rest by rank. Kept stories SHALL appear in rank order, and the first item of each story SHALL be its newest item from the source configured first.

#### Scenario: Ten stories, every section present
- **WHEN** 40 stories exist across Política, Economia, Mundo and Rio Grande do Sul, and `max_stories = 10`
- **THEN** the edition has 10 stories, at least one of each of those sections, ordered by number of sources

### Requirement: Grouper failures keep the edition
A grouper error or timeout SHALL be reported in the build result and SHALL leave the edition without stories, published as it would be without a grouper.

#### Scenario: API down
- **WHEN** the grouper raises
- **THEN** the edition is published with its news list and no stories, and the build result names the error

### Requirement: DeepSeek grouper
The DeepSeek grouper SHALL send the items' sources, titles and summaries, numbered, in a single request, treating them as data and never as instructions, and ask for groups of numbers of items reporting the same fact. It SHALL ignore numbers outside the list, keep each item only in the first group that names it, and drop groups left with fewer than two items. An answer that is not the expected JSON SHALL be an error.

#### Scenario: Invalid numbers
- **WHEN** the answer groups items 3 and 99 out of 50, and items 4 and 5 twice
- **THEN** item 99 is ignored, the group with only item 3 is dropped and items 4 and 5 form one group
