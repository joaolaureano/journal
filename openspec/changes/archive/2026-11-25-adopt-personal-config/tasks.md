# Tasks

## 1. Configuração do jornal

- [x] 1.1 Renomear `journal.example.toml` para `journal.toml` (comentário de topo explicando que é a config deste jornal e como adaptar num fork) e remover `journal.toml` do `.gitignore`; verificar com `git status` mostrando `journal.toml` rastreado e `uv run journal build` gerando o site
- [x] 1.2 Criar `tests/test_journal_toml.py` validando que `journal.toml` carrega e tem as fontes esperadas em ordem; verificar com `uv run pytest tests/test_journal_toml.py`

## 2. Documentação

- [x] 2.1 Atualizar o `README.md` (uso com `journal.toml`, fork para ter o próprio jornal) e verificar executando os comandos como escritos; `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` passam

## Workflow follow-up

- Arquivar a change e fazer commit/push.
- Apagar o repo `journal-private` (pasta local e GitHub).
