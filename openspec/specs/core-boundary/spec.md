# core-boundary Specification

## Purpose

Define os contratos que o core do journal expõe para fontes e publicadores e garante que o core continue independente de qualquer integração concreta.

## Requirements

### Requirement: Source contract
The core SHALL define a source contract: an operation that takes no arguments and returns a list of articles. Any object offering that operation SHALL be usable as a source.

#### Scenario: Fake source satisfies the contract
- **WHEN** an in-memory object exposing the fetch operation returns two articles
- **THEN** it is recognized as a source
- **AND** fetching returns those two articles

#### Scenario: Object without fetch is not a source
- **WHEN** an object does not expose the fetch operation
- **THEN** it is not recognized as a source

### Requirement: Publisher contract
The core SHALL define a publisher contract: an operation that receives an edition and returns nothing. Any object offering that operation SHALL be usable as a publisher.

#### Scenario: Fake publisher satisfies the contract
- **WHEN** an in-memory object exposing the publish operation receives an edition
- **THEN** it is recognized as a publisher

### Requirement: Core does not depend on adapters or third-party libraries
The domain, ports and app layers SHALL import only the Python standard library and other domain, ports or app modules.

#### Scenario: Boundary check passes
- **WHEN** the automated boundary check scans every module in the domain, ports and app layers
- **THEN** no import of the adapters layer, the command-line entry point or a third-party package is found

#### Scenario: Boundary violation is detected
- **WHEN** a domain, ports or app module imports the adapters layer or a third-party package
- **THEN** the automated boundary check fails and names the offending module and import

### Requirement: Source failures are reported as a source error
The core SHALL define a source error type. A source that cannot deliver its articles SHALL raise that error, so callers can handle failures from any source without knowing which adapter produced them.

#### Scenario: Caller handles failure without knowing the adapter
- **WHEN** a source fails to fetch and raises the source error
- **THEN** a caller that only knows the core contracts can catch it as the source error

### Requirement: Publish failures are reported as a publish error
The core SHALL define a publish error type. A publisher that cannot publish SHALL raise that error, so callers can handle publishing failures without knowing which adapter produced them.

#### Scenario: Caller handles failure without knowing the adapter
- **WHEN** a publisher fails and raises the publish error
- **THEN** a caller that only knows the core contracts can catch it as the publish error
