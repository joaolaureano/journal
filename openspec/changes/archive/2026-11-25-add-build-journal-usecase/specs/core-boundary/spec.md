# Spec Delta

## MODIFIED Requirements

### Requirement: Core does not depend on adapters or third-party libraries
The domain, ports and app layers SHALL import only the Python standard library and other domain, ports or app modules.

#### Scenario: Boundary check passes
- **WHEN** the automated boundary check scans every module in the domain, ports and app layers
- **THEN** no import of the adapters layer, the command-line entry point or a third-party package is found

#### Scenario: Boundary violation is detected
- **WHEN** a domain, ports or app module imports the adapters layer or a third-party package
- **THEN** the automated boundary check fails and names the offending module and import
