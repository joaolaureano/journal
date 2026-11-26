## MODIFIED Requirements

### Requirement: Built-in static site publisher type
The `static-site` publisher type SHALL take an optional `storage` table with a `type` and that storage type's options, defaulting to `{ type = "local", out = "dist" }`. As a shorthand, an `out` option SHALL mean local storage in that directory; giving both `out` and `storage` SHALL be rejected. Storage types SHALL also be pluggable, like sources and publishers, under the plugin group `journal.storages`.

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

### Requirement: Built-in local storage type
The `local` storage type SHALL take an optional `out` directory (string, default `dist`), resolved against the directory that contains the configuration file.

#### Scenario: Default output directory
- **WHEN** the local storage declares no `out`
- **THEN** the publisher writes to `dist` next to the configuration file
