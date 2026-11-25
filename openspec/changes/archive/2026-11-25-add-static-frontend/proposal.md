# Proposal

## Why

Hoje o build gera só `articles.json`; ninguém lê notícias num JSON. Falta o site em si: uma página com a lista de notícias e uma página por artigo, servíveis por qualquer hospedagem estática (S3+CloudFront depois, `file://` agora).

## What Changes

- O publisher estático passa a gerar `index.html` (lista), `articles/<id>.html` (uma página por artigo) e `style.css`, além do `articles.json`.
- Interface em português (pt-BR), HTML semântico, sem JavaScript, links relativos.
- Todo texto vindo dos feeds é escapado antes de entrar no HTML.
- Cada publicação substitui o site inteiro: páginas de artigos que saíram do feed não ficam para trás e uma publicação interrompida não deixa o site pela metade.
- **Proteção**: o publisher se recusa a substituir um diretório existente que não esteja vazio nem seja um site do journal (ex.: `--out ~`).
- Falha de publicação vira um erro definido no core; o CLI a reporta e sai com código diferente de zero.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `static-site`: adiciona páginas HTML, CSS, escape, substituição do site inteiro e proteção do diretório de saída.
- `core-boundary`: adiciona o erro de publicação ao contrato de publicação.
- `journal-build`: o comando `journal build` também reporta falha de publicação.

## Impact

- `src/journal/adapters/static_site.py` reescrito; novos templates em `src/journal/adapters/templates/`.
- `PublishError` em `src/journal/ports/publisher.py`; `src/journal/cli.py` captura o erro.
- Sem novas dependências (templates com `string.Template` da stdlib).
