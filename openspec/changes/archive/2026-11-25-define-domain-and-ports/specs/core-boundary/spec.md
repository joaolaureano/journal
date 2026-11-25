# Spec Delta

## Purpose

Define os contratos que o core do journal expõe para fontes e publicadores e garante que o core continue independente de qualquer integração concreta.

## ADDED Requirements

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
The core SHALL define a publisher contract: an operation that receives a sequence of articles and returns nothing. Any object offering that operation SHALL be usable as a publisher.

#### Scenario: Fake publisher satisfies the contract
- **WHEN** an in-memory object exposing the publish operation receives a list of articles
- **THEN** it is recognized as a publisher
- **AND** it holds exactly the articles it received, in order

### Requirement: Core does not depend on adapters or third-party libraries
The domain and ports layers SHALL import only the Python standard library and other domain or ports modules.

#### Scenario: Boundary check passes
- **WHEN** the automated boundary check scans every module in the domain and ports layers
- **THEN** no import of the adapters layer, the app layer or a third-party package is found

#### Scenario: Boundary violation is detected
- **WHEN** a domain or ports module imports the adapters layer or a third-party package
- **THEN** the automated boundary check fails and names the offending module and import
