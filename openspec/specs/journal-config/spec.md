# journal-config Specification

## Purpose

Define como o journal declara suas fontes e seu publicador num arquivo de configuração e como novos tipos de adapter passam a ser aceitos sem alterar o core.

## Requirements

### Requirement: Configuration declares sources and publisher
The configuration SHALL be a TOML file with a non-empty `[[sources]]` array and one `[publisher]` table. Each entry SHALL have a `type` and the options of that type, and sources SHALL be built in the order they are declared.

#### Scenario: Two sources and a publisher
- **WHEN** a configuration declares two `rss` sources and a `static-site` publisher
- **THEN** loading it yields two sources, in declared order, and one publisher

### Requirement: Built-in RSS source type
The `rss` source type SHALL take a required `name` (string), a required `url` (string), an optional `timeout` in seconds (number greater than 0, default 10) and an optional `full_text` (boolean, default false) that keeps the feed's full text as the article body.

#### Scenario: RSS source from configuration
- **WHEN** a source entry is `type = "rss"`, `name = "Nature"`, `url = "https://www.nature.com/nature.rss"`
- **THEN** the loaded source reads that feed and labels its articles `Nature`

#### Scenario: Full text is opt-in
- **WHEN** a source entry has no `full_text`
- **THEN** its articles have no body

#### Scenario: Invalid full_text
- **WHEN** an `rss` source has `full_text = "yes"`
- **THEN** loading fails with a configuration error naming `full_text`

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

### Requirement: New adapter types plug in by registration
Adding a source or publisher type SHALL require only registering a factory for its type name, outside the domain, ports and app layers. After registration, configurations SHALL be able to use that type like a built-in one.

#### Scenario: Registered source type is usable
- **WHEN** a factory is registered for a new source type `fake` and a configuration declares a source with `type = "fake"`
- **THEN** loading the configuration yields a source built by that factory
- **AND** no domain, ports or app module was changed

### Requirement: Invalid configuration is rejected
Loading SHALL fail with a configuration error whose message names the problem and, for an entry, its position, when the file is missing or not valid TOML, `sources` is missing or empty, `publisher` is missing, a type is unknown, or an option is missing, unknown or of the wrong type.

#### Scenario: Missing file
- **WHEN** the configuration file does not exist
- **THEN** loading fails with a configuration error naming the path

#### Scenario: Invalid TOML
- **WHEN** the configuration file is not valid TOML
- **THEN** loading fails with a configuration error

#### Scenario: No sources
- **WHEN** the configuration has no `sources` or an empty `sources` array
- **THEN** loading fails with a configuration error mentioning `sources`

#### Scenario: Missing publisher
- **WHEN** the configuration has no `publisher` table
- **THEN** loading fails with a configuration error mentioning `publisher`

#### Scenario: Unknown type
- **WHEN** a source has `type = "carrier-pigeon"`
- **THEN** loading fails with a configuration error naming that type, the entry position and the known types

#### Scenario: Missing option
- **WHEN** an `rss` source has no `url`
- **THEN** loading fails with a configuration error naming `url` and the entry position

#### Scenario: Unknown option
- **WHEN** an `rss` source has an option `ulr`
- **THEN** loading fails with a configuration error naming `ulr`

#### Scenario: Wrong option type
- **WHEN** an `rss` source has `timeout = "fast"`
- **THEN** loading fails with a configuration error naming `timeout`

### Requirement: Adapter types from installed packages
An installed package SHALL be able to provide source and publisher types by declaring entry points in the `journal.sources` and `journal.publishers` groups, named after the type and pointing at an adapter type definition. Configurations SHALL use these types exactly like built-in ones, without any change to the journal package.

#### Scenario: Plugin source type in a configuration
- **WHEN** an installed package declares a `journal.sources` entry point named `fake` and a configuration declares a source with `type = "fake"`
- **THEN** loading the configuration yields the source built by that plugin

#### Scenario: Plugin types listed as known
- **WHEN** a configuration uses an unknown type while a plugin provides type `fake`
- **THEN** the configuration error lists `fake` among the known types

### Requirement: Plugins are loaded only when used
A plugin type SHALL be loaded only when a configuration uses it. When a used plugin cannot be imported or does not point at an adapter type definition, loading SHALL fail with a configuration error naming the type and the entry point.

#### Scenario: Unused broken plugin
- **WHEN** an installed plugin fails to import and the configuration does not use its type
- **THEN** the configuration loads normally

#### Scenario: Used broken plugin
- **WHEN** the configuration uses a type whose plugin fails to import
- **THEN** loading fails with a configuration error naming the type and the entry point

#### Scenario: Entry point is not an adapter type
- **WHEN** the configuration uses a type whose entry point points at something that is not an adapter type definition
- **THEN** loading fails with a configuration error naming the type

### Requirement: Type names are unambiguous
When a configuration uses a type name provided by more than one provider, built-in or plugin, loading SHALL fail with a configuration error naming the providers instead of choosing one.

#### Scenario: Plugin reuses a built-in name
- **WHEN** a plugin declares a `journal.sources` entry point named `rss` and the configuration uses `type = "rss"`
- **THEN** loading fails with a configuration error naming the built-in and the plugin

### Requirement: Optional filter section
The configuration MAY have a `[filter]` table with `include`, `exclude` and `exclude_domains` (lists of non-empty strings), `max_articles`, `max_age_days` and `max_per_section` (positive integers), all optional. Without the table, no keyword filter, domain filter, cap or maximum age SHALL be applied. An invalid `[filter]` SHALL be rejected with a configuration error naming the offending key.

#### Scenario: Filter from configuration
- **WHEN** a configuration declares `[filter]` with `include = ["selic"]` and `max_articles = 5`
- **THEN** builds with that configuration apply that filter and cap

#### Scenario: Maximum age from configuration
- **WHEN** a configuration declares `[filter]` with `max_age_days = 2`
- **THEN** builds with that configuration drop articles older than 2 days

#### Scenario: Invalid filter option
- **WHEN** `[filter]` has `max_articles = 0`, `max_age_days = 1.5`, `include = "selic"`, `exclude_domains = [""]` or an unknown key `inclde`
- **THEN** loading fails with a configuration error naming that key

### Requirement: Timezone of editions
The configuration MAY have a top-level `timezone` with an IANA timezone name, defaulting to `America/Sao_Paulo`. It SHALL decide the date of each edition. A value that is not a string or not a known timezone SHALL be rejected with a configuration error mentioning `timezone`.

#### Scenario: Default timezone
- **WHEN** the configuration has no `timezone`
- **THEN** editions are dated in `America/Sao_Paulo`

#### Scenario: Unknown timezone
- **WHEN** `timezone = "Mars/Olympus"`
- **THEN** loading fails with a configuration error mentioning `timezone`

### Requirement: Any source can belong to a section
Every source entry, whatever its type, MAY have a `section` (non-empty string) naming the section its articles belong to. Any other value SHALL be rejected with a configuration error mentioning `section`.

#### Scenario: RSS source with section
- **WHEN** an `rss` source declares `section = "Ciência"`
- **THEN** its articles belong to the section "Ciência"

### Requirement: Built-in S3 storage type
The `s3` storage type SHALL take a required `bucket` (string) and an optional `prefix` (string, default empty). It needs boto3 installed (`journal[aws]`).

#### Scenario: S3 storage from configuration
- **WHEN** the publisher declares `storage = { type = "s3", bucket = "meu-jornal" }`
- **THEN** the static site is written to the bucket `meu-jornal`

### Requirement: Built-in local storage type
The `local` storage type SHALL take an optional `out` directory (string, default `dist`), resolved against the directory that contains the configuration file.

#### Scenario: Default output directory
- **WHEN** the local storage declares no `out`
- **THEN** the publisher writes to `dist` next to the configuration file

### Requirement: Any source can declare its kind
Every source entry, whatever its type, MAY have a `kind`, `"noticia"` or `"artigo"`, which its articles carry; without it they are news. Any other value SHALL be rejected with a configuration error mentioning `kind`.

#### Scenario: Blog as article source
- **WHEN** an `rss` source declares `kind = "artigo"`
- **THEN** its articles have kind `artigo`

#### Scenario: Invalid kind
- **WHEN** a source declares `kind = "blog"`
- **THEN** loading fails with a configuration error naming `kind`

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
