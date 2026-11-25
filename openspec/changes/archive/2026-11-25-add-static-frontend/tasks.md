# Tasks

## 1. Contrato de erro

- [x] 1.1 Adicionar `PublishError` em `src/journal/ports/publisher.py`, exportado em `journal.ports`, e verificar com teste em `tests/test_ports.py` (cenário de `specs/core-boundary`) e `tests/test_core_boundary.py` passando

## 2. Templates

- [x] 2.1 Criar `src/journal/adapters/templates/` com `base.html`, `index.html`, `article.html` e `style.css` (pt-BR, sem scripts, links relativos, modo escuro, foco visível) e verificar que `importlib.resources` os encontra (`uv run python -c "from importlib.resources import files; print(sorted(p.name for p in (files('journal.adapters') / 'templates').iterdir()))"`)

## 3. Publisher

- [x] 3.1 Reescrever `StaticSitePublisher` em `src/journal/adapters/static_site.py`: guarda do diretório, geração em `<out>.tmp`, troca de diretórios, `index.html`, `articles/<id>.html`, `style.css`, `articles.json`, escape e datas em pt-BR; verificar com `tests/test_static_site.py` cobrindo todos os cenários de `specs/static-site` (incluindo os já existentes de JSON)

## 4. CLI

- [x] 4.1 Capturar `PublishError` em `src/journal/cli.py` e verificar com teste em `tests/test_cli.py` do cenário "Publishing fails from the command line" (saída para um diretório com arquivos alheios)
- [x] 4.2 Atualizar o `README.md` (o que vai em `dist/` e a proteção do diretório) e verificar gerando o site com o comando documentado e abrindo `dist/index.html` localmente

## 5. Integração

- [x] 5.1 Rodar `uv run pytest`, `uv run ruff check .` e `uv run ruff format --check .` e verificar que tudo passa

## Workflow follow-up

- Arquivar sincronizando `static-site`, `core-boundary` (requisitos adicionados) e `journal-build` (requisito modificado).
- Abrir a próxima change: `add-config-registry`.
