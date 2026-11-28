# Tasks

Tudo local, com escritor falso e API falsa. Nenhum teste e nenhum build local chama a DeepSeek.

## 1. Domínio e porta

- [x] 1.1 Em `domain/story.py`, criar `Paragraph`, `Divergence` e `StoryText`, e dar a `Story` o campo `text`, com a validação das fontes contra os itens
- [x] 1.2 Criar `ports/writer.py` com `WriterPort.write(story) -> StoryText | None`; exportar; `FakeWriter` em `tests/fakes.py`
- [x] 1.3 Testes do domínio: texto válido; citação de fora; parágrafo sem fonte; divergência com uma versão só ou duas do mesmo item

## 2. Build

- [x] 2.1 Em `app/build.py`, aceitar `writer`; escrever as histórias escolhidas em paralelo, com prazo de 150 s; erros distintos em `story_errors`
- [x] 2.2 Testes: história com texto; escritor que falha; escritor que demora além do prazo; sem escritor, sem texto

## 3. Escritor DeepSeek

- [x] 3.1 Bloco `VOICE` no prompt do aquecimento e no da história
- [x] 3.2 `DeepSeekWriter` com a entrada numerada como dados, o JSON da resposta, a validação, o cache por `Story.id` e o orçamento `max_calls`
- [x] 3.3 Testes com API falsa: prompt com as fontes como dados; citações inválidas; parágrafo sem fonte descartado; nenhum parágrafo vira erro; divergência inválida descartada; cache sem chamada paga; orçamento esgotado

## 4. Configuração e CLI

- [x] 4.1 `max_calls` e `max_input_chars` em `[stories]` (requisito "Story writing options")
- [x] 4.2 Em `cli.py`, montar o `DeepSeekWriter` junto com o agrupador, usando o storage do publicador como cache
- [x] 4.3 Testes de config e de CLI
- [x] 4.4 Atualizar o README, com o custo

## 5. Site

- [x] 5.1 Template `story.html` e página `historias/<id>.html` para cada história com texto
- [x] 5.2 Capa com o título escrito, o primeiro parágrafo e o selo `divergência`; `stories.json` com o texto
- [x] 5.3 Estilo simples da página da história e do selo
- [x] 5.4 Testes: página com créditos, fontes por parágrafo, divergências e links; escape do texto do modelo; capa com e sem texto; `stories.json`

## 6. Verificação

- [x] 6.1 Build local com agrupador e escritor falsos sobre os itens reais, sem a DeepSeek, e conferir a capa e uma página de história
- [x] 6.2 Rodar `ruff check`, `ruff format --check`, a suíte completa e `openspec validate add-story-synthesis --strict`
