# Agrupar as notícias em histórias

## Why

O dono não se sente lendo um jornal de verdade (handoff §4.5). Hoje o site é uma lista de itens por seção, e a mesma notícia aparece várias vezes, uma por fonte. Num jornal, o que várias redações cobrem é o que importa, e cada fato aparece uma vez. Com as fontes revisadas e o coletor de hora em hora, a edição já vê o dia inteiro de cada feed. Falta juntar os itens que contam o mesmo fato e escolher as histórias do dia. É o passo 2 do handoff §5: agrupar e ranquear, mostrando "N fontes cobrem isto", ainda sem texto novo.

## What Changes

- **Histórias:** quando há um agrupador, a edição junta as notícias da janela (depois do filtro e do histórico, **antes** do limite por seção) em histórias, cada uma com os itens que contam o mesmo fato. Um item sozinho vira uma história de uma fonte só.
- **Ranking:** as histórias são ordenadas pelo número de fontes diferentes, com pelo menos uma por seção quando houver. Entram as `max_stories` primeiras (padrão 10).
- **Agrupador com LLM:** uma porta nova, `GrouperPort`, com um adaptador da DeepSeek que manda títulos e resumos numa só chamada e recebe grupos de números. A resposta é validada: números fora da lista ou repetidos são descartados.
- **Site:** a capa (`index.html`) abre com as histórias do dia. Cada uma mostra o título e o resumo do item principal, "N fontes" e um link para cada item. Abaixo vem a lista de todas as notícias, como hoje. `stories.json` guarda as histórias da edição. Os itens de uma história publicada contam como publicados no `seen.json`.
- **`[stories]` no `journal.toml`:** liga o agrupamento (`max_stories`, `model`, `timeout`). Sem a tabela, ou sem `DEEPSEEK_API_KEY`, a edição sai como hoje.

Fora do escopo: o texto da história escrito pelo LLM, as citações e as divergências (mudança `add-story-synthesis`); a diagramação da capa.

## Capabilities

### New Capabilities

- `stories`: agrupamento das notícias em histórias, ranking e o agrupador com LLM.

### Modified Capabilities

- `edition`: a edição carrega as histórias.
- `journal-config`: tabela opcional `[stories]`.
- `static-site`: histórias na capa, `stories.json` e os itens das histórias no `seen.json`.

## Impact

- Código: `domain/story.py` (novo), `domain/edition.py`, `ports/grouper.py` (novo), `app/build.py`, `adapters/deepseek.py`, `adapters/static_site.py`, `config.py`, `cli.py`, README.
- Custo quando ligado: uma chamada por edição, com ~500 títulos e resumos curtos (~35 mil tokens de entrada e ~2 mil de saída). Nos preços fora do pico da DeepSeek (US$ 0,15/M de entrada, US$ 0,60/M de saída), isso dá menos de US$ 0,01 por edição, ~US$ 0,20 por mês. A edição das 08:00 de São Paulo cai às 11:00 UTC, fora do pico.
- Nenhuma chamada real durante o desenvolvimento: tudo é testado com um agrupador falso.
