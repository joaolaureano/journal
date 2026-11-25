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
The `rss` source type SHALL take a required `name` (string), a required `url` (string) and an optional `timeout` in seconds (number, default 10).

#### Scenario: RSS source from configuration
- **WHEN** a source entry is `type = "rss"`, `name = "Nature"`, `url = "https://www.nature.com/nature.rss"`
- **THEN** the loaded source reads that feed and labels its articles `Nature`

### Requirement: Built-in static site publisher type
The `static-site` publisher type SHALL take an optional `out` directory (string, default `dist`). A relative `out` SHALL be resolved against the directory that contains the configuration file.

#### Scenario: Relative output directory
- **WHEN** a configuration file in `/site` declares `out = "public"`
- **THEN** the publisher writes to `/site/public`, regardless of the current working directory

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
