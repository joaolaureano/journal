# Diagramar a capa como um jornal

## Why

"Não me sinto lendo um jornal de verdade." As histórias já existem, mas a capa ainda é uma lista numa coluna estreita, com papel creme e rótulos em mono que o dono não gosta. Ele escolheu a referência: a hierarquia do NYT e da Folha, com tipografia moderna (como o memorization e o UOL) e as cores claras da imagem que mandou: fundo quase branco, tinta quase preta, fios finos e um vermelho de destaque.

## What Changes

- **Capa em hierarquia:** a primeira história é a manchete, com a imagem grande do feed e o crédito; as quatro seguintes são chamadas em grade; as demais, notas compactas.
- **Seções em faixas:** "Todas as notícias" continua, agora como uma faixa por seção com os itens em grade de cards; a aba Artigos usa cards horizontais.
- **Sem foto também funciona:** cards e manchete sem imagem mostram texto no lugar dela, sem quadro vazio.
- **Toda história marcada como IA na capa:** o selo `Texto por IA` vai para a linha de dados de cada história escrita, visível também nas chamadas e notas, onde o parágrafo não aparece.
- **Chapéu da seção** acima do título de cada história.
- **Menu de edições** fechado por padrão em qualquer tela, aberto pelo botão: a capa larga não cabe ao lado dele.
- **Tipografia e cores:** fontes do sistema (sem webfont), títulos em sans com espaçamento justo; tema claro só.
- Páginas de história e de notícia no mesmo estilo, numa coluna de leitura; celular e desktop.

Fora do escopo: modo escuro, rodapé, webfonts, mudar o conteúdo ou a ordem das histórias.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `static-site`: diagramação da capa, entrada de história com chapéu e selo de IA, menu fechado por padrão.
