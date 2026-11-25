# Design

## Context

Core já define `Article` e `SourcePort` (specs `article`, `core-boundary`). Destino é Lambda, onde uma chamada de rede pendurada consome o tempo máximo da função.

## Goals / Non-Goals

**Goals:**
- Um adapter `RssSource(location, name, timeout=10)` que satisfaz `SourcePort`.

**Non-Goals:**
- Cache HTTP (ETag/Last-Modified), retries, paralelismo.

## Decisions

- **`feedparser` para o parse**: lida com RSS 0.9x/1.0/2.0 e Atom, datas em vários formatos e sanitização de HTML. Escrever parser próprio sobre `xml.etree` cobriria só o caso feliz.
- **Download com `urllib.request.urlopen(location, timeout=...)` e bytes entregues ao `feedparser`**: `feedparser.parse(url)` não aceita timeout. `urlopen` também abre `file://`, então os testes usam fixtures locais pelo mesmo caminho de código. User-Agent genérico `journal/0.1`.
- **"Não é feed" = `parsed.version` vazio**: feedparser marca `bozo` até em feeds válidos com pequenos defeitos, então `bozo` sozinho descartaria feeds úteis. Um feed válido sem itens retorna lista vazia.
- **Datas**: `published_parsed`, senão `updated_parsed`; feedparser já as normaliza para UTC (`struct_time`), convertidas para `datetime` com `tzinfo=UTC`.
- **Texto puro com `html.parser.HTMLParser` da stdlib**: coleta só os nós de texto, ignorando o conteúdo de `<script>`/`<style>`, depois `html.unescape` implícito (`convert_charrefs=True`) e colapso de espaços. Regex de remoção de tags falha em atributos com `>`.
- **Entrada inválida é descartada com `logging.warning`**: um item ruim não deve esconder o resto do feed; o log mostra o que se perdeu.
- **`SourceError(Exception)` em `journal.ports.source`**: fica no core (spec `core-boundary`) para o caso de uso capturar sem importar o adapter. Erros de `urlopen` (`OSError`, que cobre `URLError` e timeout) são encadeados com `raise ... from`.

## Risks / Trade-offs

- [Feed que muda o link de um item gera artigo "novo"] → Aceito; dedup é por URL por definição.
- [Teste de timeout depende de socket local] → Servidor que só faz `listen` sem responder, timeout de 0,2 s; não usa rede externa.
