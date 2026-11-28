# Histórias que cobrem todas as fontes

## Why

Na primeira edição com histórias (28/11), a do Trabuco juntou 65 matérias e 38 nunca foram citadas: o texto tinha 5 parágrafos. O dono quer que a história inclua, na medida do possível, tudo o que as fontes trazem, reescrito numa ordem fluida. A causa eram os limites: 24 mil caracteres de fonte por história (~370 por matéria nesse caso), 2 a 6 parágrafos no prompt, 8 no código e 3 mil tokens de saída.

## What Changes

- **Prompt:** cobrir o que cada fonte acrescenta, sem repetir, agrupado por tema numa ordem fluida (fato, detalhes, reações, contexto, o que vem depois); de 3 a 12 parágrafos.
- **Atribuição do que é exclusivo:** um detalhe que só uma fonte traz é atribuído a ela no texto ("segundo fontes ouvidas pelo g1…"); o que todas dizem vai sem atribuição; o que não foi confirmado é dito. É o que o dono apontou como bom exemplo na história do Camilo Santana na Casa Civil (28/11).
- **Limites:** até 14 parágrafos e 8 mil tokens de saída; `max_input_chars = 120000` no `journal.toml`; `timeout = 180` por chamada.
- **Tempo:** as histórias são escritas todas ao mesmo tempo (10 em paralelo), com prazo de 240 s. A edição de 28/11 levou ~2 min dos 10 da Lambda.
- **Custo:** de ~US$ 0,03 para ~US$ 0,05 por edição (pior caso ~US$ 0,10), ~US$ 1,30 por mês.

## Capabilities

### Modified Capabilities

- `stories`: prazo da escrita e o que o escritor pede.
