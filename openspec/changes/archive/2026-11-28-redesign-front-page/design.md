# Design

## Uma lista, a diagramação no CSS

As histórias continuam numa única `<ol>` na ordem da edição. A posição decide o papel: `li:first-child` é a manchete, `li:nth-child(2–5)` são as chamadas, `li:nth-child(n+6)` são as notas. O HTML muda pouco (chapéu, selo de IA na linha de dados, figura com crédito só na manchete) e a ordem de leitura é a ordem do ranking, então a manchete vem primeiro também para leitores de tela.

As faixas de seção são as `<ol class="articles">` de hoje em grade (4 colunas no desktop, 2 no tablet, 1 no celular). A aba Artigos ganha a classe do tipo (`articles artigo`) para os cards horizontais.

## Sem foto

`:has(img)` decide: a manchete sem imagem ganha título maior e mais linhas de abertura; um card sem imagem mostra o resumo com mais linhas. Nenhum espaço reservado para imagem que não veio.

## Selo de IA

O título de uma história escrita também é texto do modelo. Por isso `Texto por IA` sai do parágrafo e vai para a linha de dados, que aparece em todas as entradas, inclusive nas chamadas e notas, onde o parágrafo fica escondido.

## Menu

A capa passa a ocupar até 72rem; o menu fixo aberto à esquerda cobriria a manchete. Ele fica fechado por padrão em toda tela e abre por cima do conteúdo pelo mesmo botão sem script.

## Tipografia e cores

`system-ui` (SF, Segoe, Roboto), como o memorization: sem arquivo de fonte nem requisição externa. Títulos em 650–700 com `letter-spacing: -0.025em`. Cores da referência do dono: fundo `#f6f6f7`, cards brancos, tinta `#161616`, cinza `#6b6b70` nos dados, fios `#dcdce0`, vermelho `#d92d20` nos selos e no chapéu. Só tema claro.
