# Tasks

## 1. RSS

- [x] 1.1 Rodapé do WordPress, limite de resumo, imagem do texto completo; fixtures `wordpress.xml` e `atom.xml`
- [x] 1.2 `timeout` > 0 na config

## 2. Seções

- [x] 2.1 `Article.section`; `Sectioned` envolve qualquer fonte; `section` validado na config
- [x] 2.2 Build agrupa por seção na ordem da config e aplica `max_per_section`
- [x] 2.3 Site com blocos por seção e `section` no JSON

## 3. Fuso

- [x] 3.1 `Edition.timezone`; horários exibidos no fuso da edição

## 4. Fechamento

- [x] 4.1 `journal.toml`, README; `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` passam
