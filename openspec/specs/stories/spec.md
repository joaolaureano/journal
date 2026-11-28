# stories Specification

## Purpose

Junta as notícias que contam o mesmo fato em histórias, escolhe as histórias do dia pela cobertura e define o agrupador com LLM.

## Requirements

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
The DeepSeek grouper SHALL send the items' sources, titles and summaries, numbered, in a single request, treating them as data and never as instructions, and ask for groups of items reporting the same specific fact, not the same subject or case, leaving out items in doubt. It SHALL ignore numbers outside the list, keep each item only in the first group that names it, and drop groups left with fewer than two items. An answer that is not the expected JSON SHALL be an error.

#### Scenario: Invalid numbers
- **WHEN** the answer groups items 3 and 99 out of 50, and items 4 and 5 twice
- **THEN** item 99 is ignored, the group with only item 3 is dropped and items 4 and 5 form one group

### Requirement: Written stories
When the build has a writer, it SHALL ask it, after ranking, for the text of every kept story: a title and paragraphs, each paragraph naming the items that support it, and the points where items disagree. Requests SHALL run in parallel, and stories not answered within 240 seconds SHALL be published without text. A writer error or an empty answer SHALL leave that story without text, and distinct error messages SHALL be reported in the build result.

#### Scenario: Story with text
- **WHEN** the writer answers for a kept story
- **THEN** the edition's story carries the title, the paragraphs and their supporting items

#### Scenario: Writer down
- **WHEN** the writer raises for every story
- **THEN** the edition still has its stories, without text, and the build result names the error

### Requirement: Story text supported by its items
A story text SHALL only cite items of its own story. Every paragraph SHALL cite at least one of them, and every divergence SHALL hold at least two versions from different items. The domain SHALL reject a text that breaks these rules for its story.

#### Scenario: Citation outside the story
- **WHEN** a paragraph cites an item that is not in the story
- **THEN** creating the story with that text fails

### Requirement: DeepSeek writer
The DeepSeek writer SHALL send each item's source, title, publication time in the edition's zone and text, numbered and marked as data, and ask for JSON with a title, flowing paragraphs covering what each item adds, with their sources, and divergences, which exclude values that change over the day when items were published apart. It SHALL drop invalid citations, uncited paragraphs and divergences without two distinct sources, and SHALL fail when no paragraph remains.

#### Scenario: Invalid citations
- **WHEN** the answer has a paragraph citing sources 1 and 9 for a story of two items, and a paragraph citing only 9
- **THEN** the first paragraph keeps source 1 and the second is dropped

#### Scenario: Divergence within one outlet
- **WHEN** a divergence has versions from two g1 economia items only
- **THEN** it is dropped

#### Scenario: Publication time in the edition's zone
- **WHEN** an item published at 2026-01-01 00:00 UTC is sent for an edition in America/Sao_Paulo
- **THEN** its source block reads `Publicado: 31/12/2025 21:00`

### Requirement: Writer cache and budget
The DeepSeek writer SHALL cache each answer by story in the storage, so the same group of items is written once, and SHALL stop making paid requests after `max_calls` in an edition.

#### Scenario: Same group, later revision
- **WHEN** a story with the same items is written again on a later revision
- **THEN** the text comes from the cache, without a paid request

### Requirement: Groups checked for shared words
Before turning groups into stories, the build SHALL drop from each group every item whose title shares no word of four letters or more (accents, case and common words aside) with the titles of the group's other items, with at least two of them in groups of four or more. A dropped item SHALL become a story of its own.

#### Scenario: Unrelated item in a group
- **WHEN** the grouper puts three items about Camilo Santana in the Casa Civil and one about fake ads on Black Friday in one group
- **THEN** the edition has one story with the three Camilo items and one with the Black Friday item alone
