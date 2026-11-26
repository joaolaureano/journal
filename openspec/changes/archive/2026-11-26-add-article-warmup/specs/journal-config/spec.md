## ADDED Requirements

### Requirement: Optional summarizer section
The configuration MAY have a `[summarizer]` table with `model` (string, default `deepseek-flash`), `max_calls` and `max_input_chars` (positive integers, defaults 50 and 16000) and `timeout` (positive number of seconds for the whole warm-up step, default 180). Builds SHALL use a DeepSeek summarizer only when the table exists and `DEEPSEEK_API_KEY` is set. An invalid table SHALL be rejected naming the offending key.

#### Scenario: Summarizer from configuration
- **WHEN** a configuration declares `[summarizer]` with `max_calls = 10` and `DEEPSEEK_API_KEY` is set
- **THEN** builds warm up articles with at most 10 paid calls

#### Scenario: No API key
- **WHEN** a configuration declares `[summarizer]` and `DEEPSEEK_API_KEY` is unset
- **THEN** the build publishes without warm-ups and says the key is missing

#### Scenario: Invalid summarizer option
- **WHEN** `[summarizer]` has `max_calls = 0` or an unknown key `max_call`
- **THEN** loading fails with a configuration error naming that key
