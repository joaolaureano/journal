# Design

## Context

- A edição já tem `stories` (`Story(items, section)`), ranqueadas no app. A capa mostra cada uma com o item principal e os links das fontes, e `stories.json` guarda os ids.
- O aquecimento mostra como o projeto escreve texto com o LLM: porta, adaptador DeepSeek por `urllib`, cache por chave no storage, orçamento por edição, threads com prazo e falha que só custa o texto.
- Restrições do handoff §3: texto de feed é dado; a saída do LLM entra na página só escapada; todo texto gerado é identificado como IA e creditado, com link para cada original; nenhuma afirmação é atribuída a quem não a fez; falha do LLM não derruba a edição.

## Goals / Non-Goals

**Goals:** um texto por história, em voz única, com cada parágrafo ligado às fontes que o sustentam e as divergências à vista.

**Non-Goals:** checar cada frase com uma segunda chamada; traduzir as fontes estrangeiras como etapa separada (o próprio texto já sai em português); diagramação.

## Decisions

1. **Domínio:** `StoryText(title, paragraphs, divergences)`, `Paragraph(text, sources)` e `Divergence(point, views)`, com `sources` e `views` usando os `Article.id` dos itens. `Story` ganha `text: StoryText | None = None`. O `__post_init__` da história recusa um texto que cite itens de fora, um parágrafo sem fonte ou uma divergência com menos de duas versões de itens diferentes. Assim a regra "nenhuma afirmação sem fonte do grupo" vale em todo o sistema, não só no adaptador.

2. **Porta `WriterPort.write(story) -> StoryText | None`.** O build chama em paralelo, com até 4 threads, depois do ranking, com prazo de 150 s para a etapa inteira (`STORY_TIMEOUT`). As histórias sem resposta saem sem texto. É o mesmo padrão do aquecimento.

3. **Prompt e JSON:** cada item vai numerado como `<fonte n="1" nome="g1 política">` com título e texto, dentro de uma marcação de dados. A resposta é JSON (`response_format: json_object`): `{"titulo", "paragrafos": [{"texto", "fontes": [1, 2]}], "divergencias": [{"ponto", "versoes": [{"fonte": 1, "diz": "…"}]}]}`. O adaptador valida, traduz números para ids e monta o `StoryText`. O domínio valida de novo.
   - *Alternativa:* texto livre com marcas `[1]` no meio. É mais frágil de validar e de mostrar.

4. **Voz única:** um bloco `VOICE`, com as regras de estilo (português do Brasil, frases diretas, sem adjetivos de opinião, sem inventar, atribuindo cada fato à fonte quando houver discordância), entra no prompt do aquecimento e no da história.
   - O cache do aquecimento não leva o prompt na chave, então os textos já em cache não mudam.

5. **Entrada por história:** o texto completo de cada item (o `body` como texto puro, ou o resumo), cortado para caber em `max_input_chars` (padrão 24.000) dividido entre os itens. `shortcut: corte por item, sem resumo prévio; vale resumir antes se histórias de muitas fontes ficarem rasas`.

6. **Cache por `Story.id`** em `llm-cache/story/<id>.json`, com o JSON validado. Como o id vem das chaves dos itens, a mesma história numa revisão não paga de novo. Um item novo no grupo gera um id novo, e o texto é refeito, o que é o certo. O orçamento é `max_calls` chamadas pagas por edição (padrão 10).

7. **Site:**
   - `historias/<id>.html` na pasta da edição, montado de um template novo `story.html`;
   - capa com o título escrito, o primeiro parágrafo e o selo `divergência`;
   - `stories.json` com o texto;
   - tudo que vem do modelo passa por `escape()`.

## Risks / Trade-offs

- [O LLM escrever algo que nenhuma fonte disse] → cada parágrafo mostra as fontes que o sustentam, com link, e o selo de IA fica sempre visível. A checagem frase a frase fica para uma mudança futura (handoff §4.5: a conferência é contra as fontes, não contra o mundo).
- [Prazo da Lambda] → a coleta das fontes, o agrupamento (até 120 s), a escrita (150 s) e o aquecimento (180 s) somam no pior caso perto de 500 s, ainda abaixo dos 600 s. Se apertar, rodar a escrita e o aquecimento juntos.
- [Injeção de prompt num texto de fonte] → os itens vão como dados, a resposta só pode citar números do grupo, e tudo é escapado.
