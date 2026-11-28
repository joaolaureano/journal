## ADDED Requirements

### Requirement: Optional pool section
The configuration MAY have a `[pool]` table with `hours` (positive integer, default 48), the window of earlier fetches that a source's articles are kept for. With the table, builds and collections SHALL read every source through the pool in the publisher's storage; without it, sources SHALL be read only from their feeds. An invalid table SHALL be rejected naming the offending key.

#### Scenario: Pool from configuration
- **WHEN** a configuration declares `[pool]` with `hours = 36`
- **THEN** builds receive each source's feed items plus the items stored in the last 36 hours

#### Scenario: Invalid pool option
- **WHEN** `[pool]` has `hours = 0` or an unknown key `hour`
- **THEN** loading fails with a configuration error naming that key

### Requirement: Optional path filter on every source
Every source entry, whatever its type, MAY have `paths`, a non-empty list of strings that each start with `/`. With it, the source SHALL keep only the articles whose link path starts with one of those strings, ignoring the host. Any other value SHALL be rejected with a configuration error mentioning `paths`.

#### Scenario: One general feed, one section
- **WHEN** a source has `paths = ["/politica/"]` and its feed links to `https://www.cnnbrasil.com.br/politica/a` and `https://www.cnnbrasil.com.br/esportes/b`
- **THEN** only the `/politica/a` article is kept

#### Scenario: Path without leading slash
- **WHEN** a source has `paths = ["politica"]`
- **THEN** loading fails with a configuration error mentioning `paths`
