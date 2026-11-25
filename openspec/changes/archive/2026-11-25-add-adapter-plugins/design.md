# Design

## Context

O registro atual são os dicts `SOURCE_TYPES`/`PUBLISHER_TYPES` em `src/journal/config.py`, consultados por `_build` (spec `journal-config`). O repo privado vai depender deste por caminho editável e precisa somar tipos sem editá-lo.

## Goals / Non-Goals

**Goals:**
- Plugins por empacotamento padrão do Python, sem config extra no journal.

**Non-Goals:**
- Versionamento da API de plugins, sandbox, plugins de LLM (virão com o próprio port, numa change futura).

## Decisions

- **Entry points (`importlib.metadata.entry_points(group=...)`)**: mecanismo padrão de plugins do Python. O pacote privado só declara `[project.entry-points."journal.sources"] meu-tipo = "pacote.modulo:MEU_TIPO"` no próprio `pyproject.toml`. Alternativas: módulo indicado na config (`plugins = ["x"]`), que é mais uma chave para validar e repete o que o empacotamento já resolve; ou monkeypatch dos dicts pelo privado, que é frágil e depende da ordem de import.
- **Resolução sob demanda em `_build`**: para um `type`, junta o embutido (se houver) e os entry points com aquele nome; só então chama `ep.load()`. Os nomes de entry points (sem carregar) entram na lista "known" da mensagem de tipo desconhecido.
- **Ambiguidade = erro**: com mais de um provedor, o `ConfigError` lista `built-in` e/ou `ep.value` de cada um. Escolher por precedência esconderia qual código está rodando.
- **Erros de plugin**: qualquer exceção em `ep.load()` vira `ConfigError` encadeado (`raise ... from`) com o nome do tipo e `ep.value`; resultado que não é `AdapterType` também é rejeitado.
- **Teste sem instalar pacote**: os testes substituem `config.entry_points` por uma função que devolve `EntryPoint`s reais apontando para `tests/sample_plugin.py` (que está no `sys.path` dos testes, como `fakes.py`).

## Risks / Trade-offs

- [`AdapterType` vira API pública: mudar sua forma quebra plugins] → Documentado no README como contrato; mudanças futuras passam por change OpenSpec que modifica `journal-config`.
