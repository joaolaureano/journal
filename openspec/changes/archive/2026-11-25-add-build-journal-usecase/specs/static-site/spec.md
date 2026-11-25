# Spec Delta

## Purpose

Define o que o publicador de site estático grava no diretório de saída, para que hospedagem estática e consumidores do feed JSON possam contar com um formato estável.

## ADDED Requirements

### Requirement: Articles index in JSON
Publishing SHALL write `articles.json` in the output directory, creating the directory if needed: a JSON array with one object per article, in the order received, each with `id`, `title`, `url`, `summary`, `source` and `published_at` as an ISO 8601 timestamp with UTC offset.

#### Scenario: Two articles published
- **WHEN** two articles are published to an empty output directory
- **THEN** `articles.json` holds two objects, in the same order, with all six fields

#### Scenario: Non-ASCII text
- **WHEN** an article title contains accented characters
- **THEN** `articles.json` is UTF-8 and holds the characters as written, not escaped

### Requirement: Index is replaced atomically
Publishing SHALL replace an existing `articles.json` only after the new content is completely written, so an interrupted publish never leaves a truncated index.

#### Scenario: Republish over existing index
- **WHEN** articles are published to a directory that already has an `articles.json`
- **THEN** the file afterwards holds exactly the newly published articles
