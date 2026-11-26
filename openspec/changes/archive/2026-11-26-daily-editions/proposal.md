# Proposal

## Why

O journal é um jornal: deve sair uma edição por dia (job por volta das 8h, depois na AWS), com histórico. Hoje cada build substitui o site inteiro e não há noção de data. Além disso, o publicador mistura gerar HTML com gravar em disco, o que impede reaproveitar a mesma lógica para gravar no S3.

## What Changes

- **BREAKING (layout do site):** cada build grava uma edição em `edicoes/AAAA-MM-DD/` (com `articles/`, `index.html`, `articles.json`). A raiz tem `index.html` (edição mais recente), `edicoes/index.html` (arquivo), `editions.json` (manifesto) e `style.css`.
- Edições nunca são sobrescritas: nova execução no mesmo dia vira revisão `AAAA-MM-DD-2`, `-3`...
- Ordem de gravação: arquivos da edição primeiro; `editions.json` e `index.html` por último.
- Novo objeto de domínio `Edition(date, articles)`; o publicador recebe uma edição.
- A data da edição vem do relógio no fuso configurado (`timezone`, padrão `America/Sao_Paulo`).
- Nova porta de armazenamento do site estático (`exists`, `read`, `write`) com adapter `local`; config `storage = { type = "local", out = "dist" }` (`out` direto continua como atalho). Tipos de armazenamento podem vir de plugins (`journal.storages`).
- Dependência `tzdata` para o banco de fusos funcionar em qualquer sistema.

## Capabilities

### New Capabilities
- `edition`: a edição diária como objeto de domínio.

### Modified Capabilities
- `core-boundary`: contrato do publicador recebe uma edição.
- `journal-build`: build monta a edição do dia.
- `static-site`: layout por edição, revisões, manifesto, arquivo, armazenamento plugável.
- `journal-config`: `timezone` e `storage`.

## Impact

- `domain/edition.py`, `ports/publisher.py`, `app/build.py`, `adapters/static_site.py`, `adapters/storage.py` (novo), `config.py`, `cli.py`, templates, README, `journal.toml`, testes.
- Fora de escopo: janela "desde a edição anterior" (registro de URLs vistas), armazenamento S3, Lambda e agendamento.
- Um `dist/` antigo é aceito (tem `articles.json`), mas a pasta `articles/` antiga fica órfã: apague `dist/` uma vez.
