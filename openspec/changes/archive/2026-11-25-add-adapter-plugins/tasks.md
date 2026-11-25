# Tasks

## 1. Descoberta de plugins

- [x] 1.1 Implementar a resolução de tipos em `src/journal/config.py` (embutidos + entry points `journal.sources`/`journal.publishers`, carga sob demanda, erros de plugin e de ambiguidade) e verificar com `tests/sample_plugin.py` + novos testes em `tests/test_config.py` cobrindo os cenários de `specs/journal-config` deste delta; os testes existentes de config continuam passando

## 2. Exemplo e documentação

- [x] 2.1 Renomear `journal.toml` para `journal.example.toml`, ignorar `journal.toml` no `.gitignore` (config pessoal nunca entra no repo público) e verificar com `uv run journal build --config journal.example.toml` gerando o site
- [x] 2.2 Atualizar o `README.md` (uso com o exemplo, seção "Escrevendo um plugin" com o trecho de `pyproject.toml` e a API pública) e verificar que os comandos documentados rodam como escritos

## 3. Integração

- [x] 3.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar sincronizando `journal-config`.
- `git init`, commit e publicação do repo `journal`; depois criação do repo privado.
