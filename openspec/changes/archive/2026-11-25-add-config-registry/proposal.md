# Proposal

## Why

Hoje o `journal build` só aceita um feed passado por flags, e trocar de fonte ou publisher exige editar código. O objetivo da arquitetura é que novas fontes (Google News, RSSHub, Reddit, scraping) e, depois, novos LLMs entrem sem mexer no core. Para isso as fontes e o publisher precisam ser declarados num arquivo e montados por um registro de tipos.

## What Changes

- Arquivo de configuração `journal.toml` declarando a lista ordenada de `[[sources]]` e o `[publisher]`, cada um com `type` e suas opções.
- Registro de tipos na raiz de composição: `rss` (fonte) e `static-site` (publisher) vêm registrados; um tipo novo entra registrando uma fábrica, sem alterar `domain`, `ports` ou `app`.
- Validação da config com mensagens que apontam o problema (arquivo ausente, TOML inválido, tipo desconhecido, opção ausente, desconhecida ou com tipo errado).
- **BREAKING** (só para uso local): `journal build --feed/--name/--out` é substituído por `journal build [--config journal.toml]`.
- `journal.toml` de exemplo na raiz com duas fontes RSS (Nature e ScienceDaily), provando a extensão só por configuração.
- Fora: carregar adapters de pacotes externos (entry points) para o futuro repo privado; variáveis de ambiente na config.

## Capabilities

### New Capabilities
- `journal-config`: formato do arquivo de configuração, tipos embutidos, validação e o ponto de extensão para novos tipos.

### Modified Capabilities
- `journal-build`: o comando `journal build` passa a ler fontes e publisher do arquivo de configuração.

## Impact

- Novo módulo `src/journal/config.py`; `src/journal/cli.py` alterado.
- Novo `journal.toml` na raiz; `README.md` atualizado.
- Testes do CLI reescritos para usar config; nova fixture `tests/fixtures/feed2.xml`.
- Sem novas dependências (`tomllib` é stdlib).
