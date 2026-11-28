# Tasks

Tudo local, com um agrupador falso. Nenhum teste e nenhum build local chama a DeepSeek.

## 1. Domínio e porta

- [x] 1.1 Criar `domain/story.py` com `Story(items, section)`, `id` derivado das chaves ordenadas, `lead` e `sources`; exportar em `journal.domain`
- [x] 1.2 Dar a `Edition` o campo `stories: tuple[Story, ...] = ()`
- [x] 1.3 Criar `ports/grouper.py` com `GrouperPort.group(articles) -> list[list[Article]]`; exportar em `journal.ports`; fake `FakeGrouper` em `tests/fakes.py`
- [x] 1.4 Testes do domínio: id estável e igual para os mesmos itens em outra ordem; `sources` sem repetição; edição sem histórias por padrão

## 2. Build

- [x] 2.1 Em `app/build.py`, aceitar `grouper` e `max_stories`; agrupar as notícias candidatas antes do corte por seção; itens sem grupo viram histórias de um item; cada item em uma história só; seção pela maioria, empate pela ordem configurada
- [x] 2.2 Ranking por fontes distintas e item mais novo, com a melhor de cada seção primeiro e o item principal pela ordem das fontes; `Edition.stories`
- [x] 2.3 Erro do agrupador em `BuildReport.story_errors`, edição sem histórias
- [x] 2.4 Testes: mesmo fato em três fontes; item sozinho; item em dois grupos; seção por maioria e empate; ranking com 10 de 40 e todas as seções; falha do agrupador

## 3. Agrupador DeepSeek

- [x] 3.1 Extrair `_chat` do summarizer em `adapters/deepseek.py`, sem mudar o comportamento dele (os testes atuais continuam passando)
- [x] 3.2 Criar `DeepSeekGrouper` com o prompt de itens numerados como dados, `response_format` JSON e a validação dos números
- [x] 3.3 Testes com HTTP falso: números inválidos e repetidos; JSON inválido vira erro; o prompt leva os itens dentro da marcação de dados

## 4. Configuração e CLI

- [x] 4.1 Ler `[stories]` em `config.py` (`max_stories`, `model`, `timeout`), recusando chave ou valor inválido com o nome da chave
- [x] 4.2 Em `cli.py`, montar o `DeepSeekGrouper` só com `[stories]` e `DEEPSEEK_API_KEY`, e mostrar o número de histórias e os erros no resumo; a Lambda registra os erros
- [x] 4.3 Testes de config e de CLI: tabela válida e inválida; sem chave, a edição sai sem histórias e avisa
- [x] 4.4 Documentar `[stories]` no README, com o custo

## 5. Site

- [x] 5.1 Bloco `Histórias do dia` na capa da edição e na raiz, com título, resumo, `N fontes` e links por item; título `Todas as notícias` na lista quando houver histórias
- [x] 5.2 Escrever `stories.json` e marcar no `seen.json` os itens das histórias
- [x] 5.3 Estilo do bloco em `style.css`, simples (a diagramação fica para depois)
- [x] 5.4 Testes: histórias na capa e na raiz, com escape; `stories.json`; item de história fora da lista marcado no `seen.json`; capa igual à de hoje sem histórias

## 6. Verificação

- [x] 6.1 Build local com um agrupador falso sobre os itens reais do pool, sem a DeepSeek, e conferir a capa
- [x] 6.2 Rodar `ruff check`, `ruff format --check`, a suíte completa e `openspec validate add-story-grouping --strict`
