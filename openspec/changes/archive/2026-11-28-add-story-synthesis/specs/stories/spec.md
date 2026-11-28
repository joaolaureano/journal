## ADDED Requirements

### Requirement: Written stories
When the build has a writer, it SHALL ask it, after ranking, for the text of every kept story: a title and paragraphs, each paragraph naming the items that support it, and the points where items disagree. Requests SHALL run in parallel, and stories not answered within 150 seconds SHALL be published without text. A writer error or an empty answer SHALL leave that story without text, and distinct error messages SHALL be reported in the build result.

#### Scenario: Story with text
- **WHEN** the writer answers for a story of three items
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
The DeepSeek writer SHALL send each item's source, title and text (the body as plain text, or the summary), numbered and marked as data, never as instructions, and ask for JSON with a title, paragraphs with the numbers of their sources, and divergences with each source's version. It SHALL drop citations of numbers outside the story, paragraphs left without a valid citation and divergences left with fewer than two versions, and SHALL fail when no paragraph remains.

#### Scenario: Invalid citations
- **WHEN** the answer has a paragraph citing sources 1 and 9 for a story of two items, and a paragraph citing only 9
- **THEN** the first paragraph keeps source 1 and the second is dropped

### Requirement: Writer cache and budget
The DeepSeek writer SHALL cache each answer by story in the storage, so the same group of items is written once, and SHALL stop making paid requests after `max_calls` in an edition.

#### Scenario: Same group, later revision
- **WHEN** a story with the same items is written again on a later revision
- **THEN** the text comes from the cache, without a paid request
