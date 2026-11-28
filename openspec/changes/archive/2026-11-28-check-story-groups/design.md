# Design

Um filtro em `app/build.py` (`_coherent`), aplicado a cada grupo antes de virar história. Palavras: título sem acentos, em minúsculas, de quatro letras ou mais, fora uma lista curta de palavras comuns. Em grupos de quatro ou mais, a palavra precisa aparecer em dois outros títulos, para um item solto não se segurar numa só coincidência.
