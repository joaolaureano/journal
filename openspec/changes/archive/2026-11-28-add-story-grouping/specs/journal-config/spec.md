## ADDED Requirements

### Requirement: Optional stories section
The configuration MAY have a `[stories]` table with `max_stories` (positive integer, default 10), `model` (non-empty string, default `deepseek-flash`) and `timeout` (positive number of seconds, default 120). Builds SHALL group news into stories with the DeepSeek grouper only when the table exists and `DEEPSEEK_API_KEY` is set. An invalid table SHALL be rejected naming the offending key.

#### Scenario: Stories from configuration
- **WHEN** a configuration declares `[stories]` with `max_stories = 8` and `DEEPSEEK_API_KEY` is set
- **THEN** editions have at most 8 stories

#### Scenario: Invalid stories option
- **WHEN** `[stories]` has `max_stories = 0` or an unknown key `max_story`
- **THEN** loading fails with a configuration error naming that key
