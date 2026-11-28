# Escrever cada história numa voz única

## Why

Com o agrupamento (`add-story-grouping`), a capa mostra as histórias do dia, mas cada uma ainda é o título e o resumo de uma fonte só, com links para as outras. O dono quer ler **um artigo por história**, escrito pelo LLM numa voz única, que junte o que cada fonte acrescenta e mostre onde elas discordam, com conferência contra as fontes (handoff §4.3 e §6). São os passos 3 e 4 do handoff §5.

## What Changes

- **Texto da história:** depois do ranking, cada história escolhida ganha um texto escrito pelo LLM a partir do texto completo dos seus itens: um título e parágrafos em português do Brasil, na mesma voz em todas as histórias.
- **Citações por parágrafo:** cada parágrafo traz as fontes que o sustentam. A validação descarta citações a fontes fora do grupo e parágrafos sem fonte válida. Sem nenhum parágrafo válido, a história fica sem texto e aparece como hoje.
- **Divergências:** quando as fontes discordam, o texto diz no próprio parágrafo quem diz o quê ("segundo A…; B afirma…"), e a história ganha uma lista de divergências, com o ponto e a versão de cada fonte. O LLM nunca decide quem está certo.
- **Página da história** (`historias/<id>.html`): o título, o selo "Texto gerado por IA a partir de" com o link de cada fonte, os parágrafos com suas fontes, o bloco de divergências e a lista de fontes com o link para cada original.
- **Capa:** uma história com texto mostra o título escrito, o primeiro parágrafo e um selo `divergência` quando houver, e o link leva à página da história.
- **Cache e orçamento:** o texto fica em cache por história (`llm-cache/story/`), então uma revisão no mesmo dia não paga de novo pelo mesmo grupo. `[stories]` ganha `max_calls` e `max_input_chars`.
- **Voz única:** o aquecimento dos artigos e o texto das histórias passam a seguir as mesmas regras de estilo.

Fora do escopo: uma segunda passada do LLM para conferir cada afirmação contra as fontes; a diagramação.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `stories`: texto, citações e divergências de cada história escolhida, e o escritor com LLM.
- `journal-config`: `[stories]` ganha `max_calls` e `max_input_chars`.
- `static-site`: página da história, capa com o texto escrito e `stories.json` com o texto.

## Impact

- Código: `domain/story.py`, `ports/writer.py` (novo), `app/build.py`, `adapters/deepseek.py`, `adapters/static_site.py`, `adapters/templates/`, `config.py`, `cli.py`, README.
- Custo quando ligado: 10 chamadas por edição, com ~6 mil tokens de entrada e ~700 de saída cada uma, ~US$ 0,02 por edição fora do pico. Somando o agrupamento, ~US$ 0,03 por edição, ~US$ 0,80 por mês, dentro do orçamento de US$ 5.
- Tempo: a escrita roda em paralelo, com prazo de 150 s para a etapa inteira, dentro dos 600 s da Lambda.
