# Design

## Context

`StaticSitePublisher` hoje grava só `articles.json` via arquivo temporário + `os.replace` (spec `static-site`). O CLI aceita `--out` livre, então o diretório pode ser qualquer pasta do usuário.

## Goals / Non-Goals

**Goals:**
- Site legível, acessível e sem JS, gerado só com stdlib.
- Publicação que nunca destrói nada que não seja um site do journal.

**Non-Goals:**
- Paginação, busca, feed RSS de saída, assets por fonte, internacionalização além de pt-BR.

## Decisions

- **Templates como arquivos (`templates/base.html`, `index.html`, `article.html`, `style.css`) com `string.Template`**: editáveis sem tocar em Python e sem dependência. Valores são escapados com `html.escape(quote=True)` **antes** da substituição; os fragmentos repetidos (itens da lista) são montados em Python a partir de valores já escapados. Alternativa Jinja2: autoescape melhor, mas dependência nova para três páginas.
- **Leitura dos templates com `importlib.resources.files("journal.adapters") / "templates"`**: funciona instalado como wheel (o hatch inclui todo arquivo dentro de `src/journal`).
- **Substituição do site inteiro por diretório irmão**: gera tudo em `<out>.tmp/`, depois `<out>` → `<out>.old`, `<out>.tmp` → `<out>`, remove `<out>.old`. Se a geração falhar, `<out>` não foi tocado e `<out>.tmp` é removido. Substitui o `os.replace` do `articles.json`, já que o diretório inteiro é trocado de uma vez (o requisito "Index is replaced atomically" continua atendido).
- **Guarda do diretório de saída**: antes de qualquer escrita, o caminho é resolvido (`Path.resolve()`); se existe, não está vazio e não contém `articles.json`, levanta `PublishError`. O mesmo vale para restos `<out>.tmp`/`<out>.old`, removidos só se também forem sites do journal ou estiverem vazios.
- **`PublishError(Exception)` em `journal.ports.publisher`**: simétrico a `SourceError`. Erros de `OSError` durante a escrita são encadeados nele. O CLI captura `BuildError` e `PublishError`.
- **Data em pt-BR sem `locale`**: tabela fixa de meses abreviados; `locale.setlocale` depende do sistema (Lambda não tem pt_BR) e é estado global.
- **CSS mínimo**: largura de leitura (~70ch), tipografia do sistema, `prefers-color-scheme` para modo escuro, foco visível; resumo no índice limitado a 3 linhas com `line-clamp`.

## Risks / Trade-offs

- [Entre os dois `rename` o diretório de saída não existe por um instante] → Aceito para build local/Lambda; no deploy (fora do escopo) o site é sincronizado para o S3, não servido direto do disco.
- [Falha depois de `<out>` → `<out>.old` e antes de `<out>.tmp` → `<out>`] → O site anterior continua em `<out>.old`; a próxima publicação aceita esse resto porque é um site do journal.
