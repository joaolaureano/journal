## MODIFIED Requirements

### Requirement: Built-in static site publisher type
The `static-site` publisher type SHALL take an optional `storage` table with a `type` and that storage type's options, defaulting to `{ type = "local", out = "dist" }`. As a shorthand, an `out` option SHALL mean local storage in that directory; giving both `out` and `storage` SHALL be rejected. The `local` storage type SHALL take an optional `out` directory (string, default `dist`), resolved against the directory that contains the configuration file. Storage types SHALL also be pluggable, like sources and publishers, under the plugin group `journal.storages`.

#### Scenario: Relative output directory
- **WHEN** a configuration file in `/site` declares `out = "public"`
- **THEN** the publisher writes to `/site/public`, regardless of the current working directory

#### Scenario: Storage table
- **WHEN** the publisher declares `storage = { type = "local", out = "site" }`
- **THEN** the publisher writes to `site` next to the configuration file

#### Scenario: Invalid storage
- **WHEN** the publisher declares both `out` and `storage`, or a storage with an unknown type or option
- **THEN** loading fails with a configuration error naming the problem

## ADDED Requirements

### Requirement: Timezone of editions
The configuration MAY have a top-level `timezone` with an IANA timezone name, defaulting to `America/Sao_Paulo`. It SHALL decide the date of each edition. A value that is not a string or not a known timezone SHALL be rejected with a configuration error mentioning `timezone`.

#### Scenario: Default timezone
- **WHEN** the configuration has no `timezone`
- **THEN** editions are dated in `America/Sao_Paulo`

#### Scenario: Unknown timezone
- **WHEN** `timezone = "Mars/Olympus"`
- **THEN** loading fails with a configuration error mentioning `timezone`
