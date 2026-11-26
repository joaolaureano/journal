## ADDED Requirements

### Requirement: Summarizer key from SSM
When `DEEPSEEK_API_KEY` is unset and `JOURNAL_DEEPSEEK_KEY_PARAMETER` names an SSM parameter, the handler SHALL read that parameter with decryption and use it as the key. If the read fails, it SHALL log the reason and build without warm-ups. The deployment SHALL set that variable to `/<name>/deepseek-api-key` and allow the function to read only that parameter.

#### Scenario: Key in SSM
- **WHEN** the handler runs with `JOURNAL_DEEPSEEK_KEY_PARAMETER` set and the parameter readable
- **THEN** the build uses the parameter's value as `DEEPSEEK_API_KEY`

#### Scenario: Parameter missing
- **WHEN** the parameter cannot be read
- **THEN** the edition is published without warm-ups and the reason is logged
