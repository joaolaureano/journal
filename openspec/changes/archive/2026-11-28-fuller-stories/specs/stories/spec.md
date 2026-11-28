## MODIFIED Requirements

### Requirement: Written stories
When the build has a writer, it SHALL ask it, after ranking, for the text of every kept story: a title and paragraphs, each paragraph naming the items that support it, and the points where items disagree. Requests SHALL run in parallel, and stories not answered within 240 seconds SHALL be published without text. A writer error or an empty answer SHALL leave that story without text, and distinct error messages SHALL be reported in the build result.

#### Scenario: Story with text
- **WHEN** the writer answers for a kept story
- **THEN** the edition's story carries the title, the paragraphs and their supporting items

#### Scenario: Writer down
- **WHEN** the writer raises for every story
- **THEN** the edition still has its stories, without text, and the build result names the error

### Requirement: DeepSeek writer
The DeepSeek writer SHALL send each item's source, title and text, numbered and marked as data, and ask for JSON with a title, paragraphs covering what each item adds in a flowing order, with the numbers of their sources, and divergences: only incompatible statements about the same fact, naming in a paragraph only sources it cites. It SHALL drop invalid citations, uncited paragraphs and divergences without two distinct sources, and SHALL fail when no paragraph remains.

#### Scenario: Invalid citations
- **WHEN** the answer has a paragraph citing sources 1 and 9 for a story of two items, and a paragraph citing only 9
- **THEN** the first paragraph keeps source 1 and the second is dropped

#### Scenario: Divergence within one outlet
- **WHEN** a divergence has versions from two g1 economia items only
- **THEN** it is dropped
