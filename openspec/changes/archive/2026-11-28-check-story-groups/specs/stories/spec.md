## ADDED Requirements

### Requirement: Groups checked for shared words
Before turning groups into stories, the build SHALL drop from each group every item whose title shares no word of four letters or more (accents, case and common words aside) with the titles of the group's other items, with at least two of them in groups of four or more. A dropped item SHALL become a story of its own.

#### Scenario: Unrelated item in a group
- **WHEN** the grouper puts three items about Camilo Santana in the Casa Civil and one about fake ads on Black Friday in one group
- **THEN** the edition has one story with the three Camilo items and one with the Black Friday item alone
