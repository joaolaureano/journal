# Spec Delta

## ADDED Requirements

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
