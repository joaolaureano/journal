# Tasks

## 1. Domínio e build

- [x] 1.1 Em `domain/article.py`, adicionar `evergreen: bool = False`
- [x] 1.2 Em `app/build.py`, fazer `_in_window` ignorar `max_age_days` para artigos `evergreen`, mantendo o corte de datas no futuro
- [x] 1.3 Testes: artigo sem `evergreen` não é atemporal; artigo atemporal de 2017 entra com `max_age_days = 2`; atemporal no futuro sai; atemporal já publicado sai pelo histórico

## 2. Fonte de arquivo

- [x] 2.1 Criar `adapters/archive.py` com `ArchiveSource(location, name, pages, timeout, today)`, que escolhe página e post pela data, lê a página com `RssSource(full_text=True)` e devolve o post com `evergreen=True`
- [x] 2.2 Testes em `tests/test_archive_source.py` com feeds de fixture em arquivos: mesmo dia, mesmo post; dias seguidos, páginas diferentes; `paged` somado a uma query existente; página ausente vira `SourceError`

## 3. Configuração e fontes

- [x] 3.1 Registrar o tipo `rss-archive` em `config.py`, com `name`, `url`, `pages` (inteiro positivo) e `timeout` opcional
- [x] 3.2 Testes de config: fonte válida; `pages = 0` recusado citando `pages`
- [x] 3.3 Documentar `rss-archive` no README
- [x] 3.4 Em `journal.toml`, adicionar a seção "Papers" com o The Morning Paper (`pages = 108`, `kind = "artigo"`) e conferir com uma leitura real e um build local sem a DeepSeek

## 4. Verificação

- [x] 4.1 Rodar `ruff check`, `ruff format --check`, a suíte completa e `openspec validate add-classic-paper --strict`
