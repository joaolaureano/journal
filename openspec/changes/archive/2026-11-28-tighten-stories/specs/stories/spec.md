## MODIFIED Requirements

### Requirement: News grouped into stories
When the build has a grouper, it SHALL hand it every news item (kind `noticia`) that passed the time window, the filter and the history, before the per-section limit, and turn its answer into stories: each group of items becomes one story, and every item in no group becomes a story of its own. An item SHALL belong to at most one story. A story's section SHALL be its lead item's section, so a section configured last, like a regional one, keeps only stories that no earlier section covered.

#### Scenario: Same fact, three outlets
- **WHEN** the grouper puts the g1, CNN Brasil and JOTA items about the same STF decision in one group
- **THEN** the edition has one story with those three items

#### Scenario: Item left alone
- **WHEN** an item is in no group
- **THEN** it becomes a story with that item only

#### Scenario: Many items from one regional outlet
- **WHEN** a story has three items from O Sul (Rio Grande do Sul) and one each from g1 política and JOTA (Política)
- **THEN** its section is Política

### Requirement: DeepSeek grouper
The DeepSeek grouper SHALL send the items' sources, titles and summaries, numbered, in a single request, treating them as data and never as instructions, and ask for groups of items reporting the same specific fact, not the same subject or case, leaving out items in doubt. It SHALL ignore numbers outside the list, keep each item only in the first group that names it, and drop groups left with fewer than two items. An answer that is not the expected JSON SHALL be an error.

#### Scenario: Invalid numbers
- **WHEN** the answer groups items 3 and 99 out of 50, and items 4 and 5 twice
- **THEN** item 99 is ignored, the group with only item 3 is dropped and items 4 and 5 form one group

### Requirement: DeepSeek writer
The DeepSeek writer SHALL send each item's source, title and text, numbered and marked as data, and ask for JSON with a title, paragraphs with the numbers of their sources, and divergences: only incompatible statements about the same fact, naming in a paragraph only sources it cites. It SHALL drop citations of numbers outside the story, paragraphs left without a valid citation and divergences without versions from two distinct sources, and SHALL fail when no paragraph remains.

#### Scenario: Invalid citations
- **WHEN** the answer has a paragraph citing sources 1 and 9 for a story of two items, and a paragraph citing only 9
- **THEN** the first paragraph keeps source 1 and the second is dropped

#### Scenario: Divergence within one outlet
- **WHEN** a divergence has versions from two g1 economia items only
- **THEN** it is dropped
