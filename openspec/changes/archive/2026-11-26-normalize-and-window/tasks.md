# Tasks

## 1. Build

- [x] 1.1 `dedup_key` no core (só stdlib) e dedup por ela; testes de variantes de URL e de query significativa
- [x] 1.2 Relógio injetável no `BuildJournal`; `max_age_days` e descarte de datas > agora + 1 dia; testes
- [x] 1.3 Capturar qualquer `Exception` por fonte e reportar como erro de fonte; testes

## 2. Configuração

- [x] 2.1 `[filter] max_age_days` validado como inteiro positivo e repassado pela CLI; testes
- [x] 2.2 README atualizado; `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` passam
