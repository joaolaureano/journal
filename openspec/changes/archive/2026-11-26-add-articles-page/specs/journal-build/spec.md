# Spec Delta

## MODIFIED Requirements

### Requirement: Number of articles per section can be capped
When a maximum per section is configured, the build SHALL keep at most that many of the newest articles of each section and kind (articles without section count as one section; news and articles of a section are counted apart), before applying the overall cap.

#### Scenario: Busy section is capped
- **WHEN** the maximum per section is 2, section "Busy" has articles at 09:00, 10:00 and 11:00 and section "Calm" one at 08:00
- **THEN** the edition holds the "Busy" articles of 11:00 and 10:00 and the "Calm" one

#### Scenario: News do not push articles out
- **WHEN** the maximum per section is 2 and section "Ciência" has three news and one article
- **THEN** the edition holds the two newest news and the article of "Ciência"
