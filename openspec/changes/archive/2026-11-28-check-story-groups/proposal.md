# Conferir os grupos do agrupador por palavras em comum

## Why

O dono gosta das histórias que juntam várias matérias, mas não quer coisas completamente diferentes juntas. Nas rodadas reais de 28/11, mesmo com o prompt mais estrito, o agrupador ainda juntava itens de outro fato (o pacote de crédito do BC na história do dólar, anúncios falsos da Black Friday na do Camilo, o Alckmin na do ajuste fiscal).

## What Changes

- Depois do agrupador, cada item precisa ter no título uma palavra em comum com os títulos das outras matérias do grupo (com duas delas, em grupos de quatro ou mais). O item que não tem sai do grupo e vira história sozinho. Sem LLM e sem custo.

Testado nos grupos reais da 1ª rodada: tira os itens de fato diferente e nenhuma matéria legítima. Itens do mesmo assunto (Lotomania com Mega-Sena) ainda passam; esse ajuste fica com o prompt. Uma variante que ignorava palavras comuns no dia foi descartada: "Trabuco", comum por causa da própria história, derrubava o grupo inteiro.

## Capabilities

### Modified Capabilities

- `stories`: conferência dos grupos por palavras em comum.
