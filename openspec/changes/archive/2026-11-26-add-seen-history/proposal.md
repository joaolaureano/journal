# Proposal

## Why

Com uma edição por dia, uma notícia que continua no feed reaparece na edição seguinte. Cada edição deve trazer só o que saiu desde a do dia anterior. Isso também evita gastar LLM com o que já foi publicado.

## What Changes

- Nova porta `HistoryPort.published_before(day)`: chaves das notícias publicadas pela primeira vez em edições de dias anteriores.
- O build descarta essas notícias (antes da janela de tempo, do filtro e do limite) e informa quantas descartou.
- O site estático implementa a porta com `seen.json` (chave → data da primeira edição), gravado antes do manifesto; entradas com mais de 90 dias são esquecidas.
- `dedup_key` passa para o domínio, como `Article.key`, para core e adapters usarem a mesma identidade.
- Revisões do mesmo dia refazem o dia inteiro (só dias anteriores contam).

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `core-boundary`: contrato de histórico.
- `journal-build`: descarte do que já saiu em dias anteriores.
- `static-site`: `seen.json`.

## Impact

- `domain/article.py`, `ports/history.py` (novo), `app/build.py`, `adapters/static_site.py`, `cli.py`, README, testes.
