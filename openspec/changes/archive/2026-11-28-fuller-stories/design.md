# Design

- Os limites crescem com o tamanho da história: o texto das fontes continua dividido entre as matérias, mas o total sobe para 120 mil caracteres, então uma história de 65 matérias manda ~1.800 caracteres de cada uma, e uma de 4 manda o texto inteiro.
- Saída de até 8 mil tokens leva cerca de um minuto; por isso as 10 histórias rodam juntas (a DeepSeek aceita milhares de requisições simultâneas) e o prazo do passo sobe para 240 s, abaixo dos 600 s da Lambda.
