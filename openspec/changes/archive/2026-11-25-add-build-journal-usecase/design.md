# Design

## Context

Core tem `Article`, `SourcePort`, `PublisherPort`, `SourceError`; existe `RssSource` (specs `article`, `core-boundary`, `rss-source`). Ainda não há publisher concreto nem ponto de entrada.

## Goals / Non-Goals

**Goals:**
- Caso de uso puro (só core), testável com os fakes existentes em `tests/fakes.py`.
- Um ponto de composição (CLI) que liga adapters concretos ao caso de uso.

**Non-Goals:**
- Paralelismo entre fontes, retries, limite de quantidade de artigos.
- Leitura de config (change `add-config-registry`).

## Decisions

- **`BuildJournal(sources, publisher).run() -> BuildReport`** em `journal/app/build.py`. `BuildReport` (dataclass) traz `articles` publicados e `errors` (`SourceError`s capturados). `BuildError` quando nenhuma fonte teve sucesso. Retornar relatório em vez de só logar deixa o CLI (e depois o Lambda) decidir como mostrar.
- **Dedup via `dict` indexado pela URL com `setdefault`**: preserva a primeira ocorrência e a ordem de inserção sem código extra.
- **Ordenação `sorted(key=lambda a: (-timestamp, url))`**: `published_at` é sempre aware (spec `article`), então `timestamp()` é comparável entre fontes.
- **CLI em `journal/cli.py`, fora das camadas do core**: é a raiz de composição (adapter "driving"), o único lugar que importa adapters concretos e o caso de uso juntos. `argparse` com subcomando `build`; entry point `journal = "journal.cli:main"`. `main(argv)` recebe argumentos para ser testável em processo.
- **Erros no stderr, resumo no stdout; saída 1 em `BuildError`**: `argparse` já usa 2 para uso incorreto.
- **`StaticSitePublisher(out_dir)` em `journal/adapters/static_site.py`**: grava `articles.json` em arquivo temporário no mesmo diretório e faz `os.replace` (atômico no mesmo filesystem). `json.dumps(..., ensure_ascii=False, indent=2)`, `published_at.isoformat()`.
- **Teste de fronteira**: `CORE_LAYERS` passa a incluir `app`; qualquer `journal.*` fora de domain/ports/app (adapters, cli) é proibido.

## Risks / Trade-offs

- [Build parcial publica site com menos fontes] → Aceito: as falhas ficam no relatório e no stderr; publicar vazio por uma falha total é o caso realmente destrutivo e está bloqueado.
- [Flags `--feed/--name` vão mudar na change 6] → Registrado como requisito; a change 6 o modifica explicitamente.
