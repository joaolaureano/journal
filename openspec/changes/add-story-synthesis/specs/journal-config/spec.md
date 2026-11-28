## ADDED Requirements

### Requirement: Story writing options
The `[stories]` table MAY also have `max_calls` (positive integer: paid writing requests per edition, default 10) and `max_input_chars` (positive integer: item text sent per story, default 24000). Builds SHALL write the stories with DeepSeek under the same conditions as they group them: the table exists and `DEEPSEEK_API_KEY` is set. An invalid value SHALL be rejected naming the key.

#### Scenario: Writing budget
- **WHEN** `[stories]` has `max_calls = 5`
- **THEN** at most 5 stories per edition get a paid written text

#### Scenario: Invalid writing option
- **WHEN** `[stories]` has `max_input_chars = 0`
- **THEN** loading fails with a configuration error naming `max_input_chars`
