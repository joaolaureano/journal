# Proposal

## Why

O jornal só lê duas fontes de ciência. O dono quer também jornais brasileiros (com foco no RS) e fontes de tecnologia/"hacker". Todas têm feed RSS/Atom, direto ou via busca do Google News, então o adapter `rss` existente basta.

## What Changes

- `journal.toml` passa de 2 para 20 fontes, agrupadas por tema (ciência, Brasil, RS, tecnologia).
- GZH, Jornal do Comércio e Correio do Povo não publicam RSS próprio: entram como busca do Google News restrita ao site (`q=site:<domínio>`).
- `tests/test_journal_toml.py` deixa de fixar a lista exata de fontes: valida que o arquivo carrega e tem ao menos uma fonte, com nomes únicos. Adicionar ou remover um feed passa a ser só editar o `journal.toml`.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
<!-- Nenhuma: muda só configuração e um teste. A change declara skip_specs: true. -->

## Impact

- `journal.toml`, `tests/test_journal_toml.py`.
- O build faz 20 requisições em sequência. O Google News responde HTTP 429 se receber muitas requisições em poucos segundos; o build já tolera falha por fonte, então nesse caso só aquela fonte fica de fora.
