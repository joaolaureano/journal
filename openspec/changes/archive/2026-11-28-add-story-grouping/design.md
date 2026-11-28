# Design

## Context

- `BuildJournal.run()` junta os itens das fontes, aplica a janela de tempo, o filtro e o histórico, ordena, corta por seção (`max_per_section`) e por total, ordena por seção e chama o aquecimento dos artigos. O resultado é uma `Edition(date, articles, timezone)`.
- O aquecimento já mostra o padrão de IA no projeto: porta em `ports/`, adaptador DeepSeek por `urllib` em `adapters/deepseek.py`, fake nos testes, orçamento e timeout, e falha que nunca derruba a edição.
- O `StaticSitePublisher` escreve `articles.json`, as páginas da edição, o `seen.json` e o `index.html` da raiz por último.
- O handoff §6 decidiu o ranking (mais fontes primeiro, pelo menos uma por seção), que histórias de uma fonte só entram e que os itens originais continuam acessíveis numa lista "todas as notícias".

## Goals / Non-Goals

**Goals:** juntar o mesmo fato de várias fontes numa história, escolher as 10 do dia e mostrá-las na capa, com a lista completa logo abaixo.

**Non-Goals:** texto escrito pelo LLM (próxima mudança), classificar por tema com o LLM (as seções já são os temas, porque cada fonte entra numa seção), diagramação.

## Decisions

1. **`Story` no domínio, `Edition.stories` com padrão vazio.** `Story(items, section)`, com `id` derivado das chaves ordenadas dos itens e propriedades `lead` (primeiro item) e `sources` (fontes distintas, na ordem dos itens). A próxima mudança acrescenta o texto. O padrão vazio mantém todas as edições e testes de hoje.

2. **`GrouperPort.group(articles) -> list[list[Article]]`.** A porta fala em artigos. O adaptador numera os itens para o LLM, o que dá menos tokens e menos alucinação que ids de 16 dígitos, e traduz de volta. O LLM só devolve os grupos de 2 ou mais. O resto vira história de um item no app, então um LLM que esquece itens nunca os some da edição.
   - *Alternativa:* agrupar por similaridade de títulos, sem LLM. A medição de 2026-11-27 mostrou que ela erra para menos: fontes diferentes escrevem títulos diferentes para o mesmo fato.

3. **O agrupamento entra antes do corte por seção.** As histórias usam todas as notícias candidatas (handoff §4.5: o corte vale depois de agrupar). A lista "todas as notícias" continua com `max_per_section`, como hoje.

4. **Ranking no app, sem LLM.** Chave `(-fontes distintas, -data do item mais novo)`. Primeiro entra a melhor história de cada seção, na ordem configurada, até `max_stories`. Depois entram as melhores que sobraram. O conjunto final é mostrado na ordem do ranking. O item principal é o mais novo da fonte configurada primeiro, o que dá preferência às fontes de grande imprensa que abrem cada seção.

5. **Uma chamada só, sem cache.** ~500 itens com título e resumo cortado em 200 caracteres cabem numa chamada (~35 mil tokens). Uma revisão no mesmo dia traz itens novos, então um cache pelo conjunto de itens quase nunca acertaria. `shortcut: sem cache do agrupamento; vale cachear por conjunto de chaves se as revisões ficarem frequentes`.

6. **Falha isolada.** Erro ou timeout do agrupador vai para `BuildReport.story_errors`, e a edição sai sem histórias. O timeout é o do HTTP (`[stories] timeout`).

7. **Refatorar o HTTP da DeepSeek.** O `_ask` do summarizer vira uma função `_chat(api_key, model, messages, max_tokens, timeout, json_mode)`, usada pelos dois. O agrupador usa `response_format: json_object`.

8. **Site.** A capa ganha um bloco `Histórias do dia` antes da lista de seções, que ganha o título `Todas as notícias`. A página de cada item já existe e serve de destino dos links. `stories.json` fica ao lado do `articles.json`. O `_seen_json` também marca os itens das histórias.

9. **Ligado por config, desligado no `journal.toml`.** `[stories]` liga o agrupamento. O dono decide quando gastar, e enquanto isso tudo roda com o agrupador falso.

## Risks / Trade-offs

- [O LLM juntar fatos diferentes] → a capa mostra cada fonte com link, então o erro fica visível. A síntese da próxima mudança cita quem disse o quê.
- [A chamada estourar o tempo com muitos itens] → timeout de 120 s; a edição sai sem histórias.
- [Injeção de prompt num título] → os itens vão como dados, a resposta só pode citar números da lista, e o título mostrado é o do feed, escapado.
