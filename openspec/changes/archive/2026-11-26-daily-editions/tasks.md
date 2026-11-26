# Tasks

## 1. Domínio e build

- [x] 1.1 `Edition(date, articles)` no domínio; `PublisherPort.publish(edition)`
- [x] 1.2 `BuildJournal` monta a edição com a data no fuso configurado; teste de virada de dia em São Paulo

## 2. Armazenamento

- [x] 2.1 `StoragePort` (`exists`, `read`, `write`) e `LocalStorage` com escrita atômica, trava contra diretório alheio e contra chave fora da raiz

## 3. Site estático

- [x] 3.1 Edição em `edicoes/<data>[-<revisão>]/`, nunca sobrescrita; manifesto `editions.json`; arquivo `edicoes/index.html`; `index.html` da raiz = edição mais recente
- [x] 3.2 Ordem: edição, `style.css`, arquivo, manifesto, `index.html`; teste de falha no meio mantém raiz e manifesto
- [x] 3.3 Testes de revisão, manifesto perdido, manifesto corrompido, site antigo aceito

## 4. Configuração e CLI

- [x] 4.1 `timezone` (padrão `America/Sao_Paulo`), `storage` com registro e plugins (`journal.storages`), `out` como atalho; dependência `tzdata`
- [x] 4.2 CLI informa a data da edição; README e `journal.toml` atualizados; `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam
