# Proposal

## Why

O projeto vai ser dividido em dois repositórios: este, que será aberto ao público com o core e os adapters genéricos, e um privado com as integrações pessoais. Hoje um tipo novo de fonte ou publisher só entra editando `src/journal/config.py`, o que obrigaria o repo privado a modificar o público. As integrações precisam vir de pacotes instalados separadamente.

## What Changes

- Tipos de fonte e de publisher passam a ser descobertos em pacotes instalados, pelos grupos de entry points `journal.sources` e `journal.publishers`; o nome do entry point é o `type` usado na config.
- Plugins só são carregados quando a config usa aquele tipo; um plugin quebrado vira erro de configuração que aponta o plugin.
- Um `type` oferecido por mais de um provedor (embutido ou plugin) é rejeitado, nunca resolvido em silêncio.
- `journal.toml` (fontes pessoais) sai do repo e vira `journal.example.toml`, genérico; o README ganha a seção "Escrevendo um plugin".

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `journal-config`: adiciona descoberta de tipos em pacotes instalados, carregamento sob demanda e rejeição de nomes ambíguos.

## Impact

- `src/journal/config.py` (descoberta via `importlib.metadata.entry_points`, stdlib).
- Novo módulo de teste com um plugin de exemplo.
- `journal.toml` → `journal.example.toml`; `README.md`.
- API pública para autores de plugin: `journal.config.AdapterType`, `journal.domain.Article`, `journal.ports`.
