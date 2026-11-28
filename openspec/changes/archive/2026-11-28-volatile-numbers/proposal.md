# Números voláteis não são divergência

## Why

O dono apontou: cotação, bolsa, número de mortos e outros dados que mudam ao longo do dia não podem virar divergência só porque um jornal publicou antes de o número mudar. O escritor nem recebia a hora de publicação de cada matéria, então não tinha como saber qual número era o mais recente.

## What Changes

- Cada fonte chega ao escritor com a hora de publicação, no fuso da edição (`Publicado: 27/11/2026 17:42`).
- O prompt trata esses dados como retrato de um momento: entre fontes de horas diferentes, é atualização; o texto usa o mais recente e diz de quando e de quem ("às 17h, segundo o g1…"). Só é divergência quando fontes publicadas perto uma da outra discordam sobre o mesmo momento.

## Capabilities

### Modified Capabilities

- `stories`: hora de publicação na entrada do escritor e regra dos dados voláteis.
