# Proposal

## Why

O plano de dois repositórios (público + privado) foi revisto: o journal é um jornal pessoal só com RSS, sem segredos, e quem quiser outro jornal faz fork e ajusta. Um repositório único é mais simples, e a configuração pessoal (lista de feeds) não é sensível.

## What Changes

- `journal.toml` com as fontes do jornal volta a ser versionado; `journal.example.toml` é removido e `journal.toml` sai do `.gitignore`.
- Teste que garante que o `journal.toml` do repositório continua válido (vindo do repo privado, que será apagado).
- README: o uso passa a ser "edite `journal.toml` e rode `journal build`"; fork como forma de ter o próprio jornal.
- O mecanismo de plugins continua: permite distribuir adapters como pacote sem fork.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
<!-- Nenhuma: muda só arquivos de configuração, teste e documentação. A change declara skip_specs: true. -->

## Impact

- `journal.toml` (novo, versionado), `journal.example.toml` (removido), `.gitignore`, `README.md`, `tests/test_journal_toml.py`.
- Repo `journal-private` (GitHub e pasta local) deixa de existir após esta change.
