## ADDED Requirements

### Requirement: Articles are grouped by section
The edition's articles SHALL be grouped by section, in the order in which each section's first source is configured, with articles without section last; inside a group they keep the newest-first order.

#### Scenario: Section order follows the configuration
- **WHEN** sources are configured as "Tecnologia", one without section, then "Ciência"
- **THEN** the edition lists the "Tecnologia" articles, then the "Ciência" ones, then those without section

### Requirement: Number of articles per section can be capped
When a maximum per section is configured, the build SHALL keep at most that many of the newest articles of each section (articles without section count as one section), before applying the overall cap.

#### Scenario: Busy section is capped
- **WHEN** the maximum per section is 2, section "Busy" has articles at 09:00, 10:00 and 11:00 and section "Calm" one at 08:00
- **THEN** the edition holds the "Busy" articles of 11:00 and 10:00 and the "Calm" one
