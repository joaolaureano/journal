# Design

## Context

O CLI (`src/journal/cli.py`) é a raiz de composição e hoje instancia `RssSource` e `StaticSitePublisher` direto a partir de flags (spec `journal-build`). O core (`domain`, `ports`, `app`) não pode importar adapters (spec `core-boundary`).

## Goals / Non-Goals

**Goals:**
- Fontes e publisher montados a partir de dados; um tipo novo = uma entrada no registro.

**Non-Goals:**
- Descoberta de adapters em pacotes externos (entry points), interpolação de variáveis de ambiente, múltiplos publishers.

## Decisions

- **TOML via `tomllib`**: stdlib desde 3.11, sem dependência. YAML exigiria PyYAML e tem armadilhas de tipagem implícita (`no` → `False`).
- **Registro em `src/journal/config.py`, fora do core**: dois dicts, `SOURCE_TYPES` e `PUBLISHER_TYPES`, de nome do tipo → `AdapterType(build, required, optional)`. `required`/`optional` mapeiam opção → tipo esperado; `build(options, config_dir)` devolve o adapter. Registrar um tipo é inserir no dict. Alternativa decorator/plugin: mais indireção para o mesmo efeito enquanto tudo vive num repo só.
- **Validação genérica a partir do esquema de cada tipo**: o loader checa `type`, opções ausentes, desconhecidas e de tipo errado antes de chamar `build`, então cada fábrica recebe opções já válidas. `bool` é rejeitado onde se espera número (em Python, `bool` é subclasse de `int`).
- **Posição da entrada nas mensagens como `source #N` (contando de 1)**: é o que a pessoa vê ao contar blocos `[[sources]]` no arquivo.
- **`ConfigError(Exception)` em `journal.config`**: erro da raiz de composição, não do core; o CLI o captura junto com `BuildError` e `PublishError`.
- **`out` relativo ao diretório do arquivo de config**: o build gera o mesmo lugar não importa de onde é chamado (cron/Lambda).
- **CLI `journal build [--config PATH]`, default `journal.toml`**: as flags `--feed/--name/--out` saem; manter as duas formas duplicaria caminhos de código e testes.

## Risks / Trade-offs

- [Quebra do uso local com `--feed`] → Projeto ainda sem usuários; README e exemplo atualizados na mesma change.
- [Repo privado futuro precisará registrar tipos sem editar `config.py`] → Inserir em `SOURCE_TYPES` já funciona a partir de outro módulo; entry points ficam para quando o repo for dividido.
