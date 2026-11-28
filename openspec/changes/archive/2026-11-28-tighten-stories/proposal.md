# Apertar o agrupamento e as divergências das histórias

## Why

A primeira rodada real (28/11) mostrou cinco problemas antes de ligar `[stories]` em produção: grupos por assunto e não por fato (caso Master, loterias diferentes, itens soltos de outro tema), divergências que não são divergências (arredondamento, medições em horários diferentes, estimativa contra resultado, fontes que concordam), um parágrafo nomeando uma fonte que não cita, histórias nacionais classificadas como "Rio Grande do Sul" porque o O Sul publica muitas matérias nacionais, e a capa repetindo o nome da mesma fonte dezenas de vezes.

## What Changes

- **Agrupamento:** o prompt define "mesmo fato" com contraexemplos e pede para não juntar na dúvida.
- **Escrita:** o prompt diz o que não é divergência, pede só as versões que conflitam e só nomeia no texto as fontes citadas no parágrafo.
- **Divergência com duas fontes:** o escritor descarta divergências cujas versões não venham de pelo menos duas fontes distintas.
- **Seção da história:** a da matéria principal (o veículo configurado primeiro), não a que tem mais itens. Contar fontes distintas, tentado antes, ainda deixava notícia nacional em "Rio Grande do Sul" quando três veículos gaúchos a cobriam.
- **Capa:** um link por fonte distinta, para a primeira matéria dela na história.

## Capabilities

### Modified Capabilities

- `stories`: seção da matéria principal; prompts do agrupador e do escritor; divergência com duas fontes.
- `static-site`: um link por fonte na entrada da história.
