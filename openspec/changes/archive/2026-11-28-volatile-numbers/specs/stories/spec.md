## MODIFIED Requirements

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
