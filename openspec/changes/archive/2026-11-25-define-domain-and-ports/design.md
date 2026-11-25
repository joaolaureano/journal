# Design

## Context

O pacote `journal` existe com as camadas vazias (change `setup-project`). Requisitos em `specs/article` e `specs/core-boundary`.

## Goals / Non-Goals

**Goals:**
- Entidade e contratos só com stdlib, prontos para os adapters das próximas changes.

**Non-Goals:**
- Normalização de texto (HTML no summary, espaços): responsabilidade do adapter que lê a fonte.
- Repositório de artigos / persistência.

## Decisions

- **`@dataclass(frozen=True)` para `Article`**: imutabilidade e igualdade de graça. `id` é `field(init=False)` calculado em `__post_init__` (via `object.__setattr__`). Alternativa pydantic: dependência externa no core, proibida por `core-boundary`.
- **`id = sha256(url).hexdigest()[:16]`**: determinístico, só hex minúsculo (seguro para nome de arquivo em `dist/`), 64 bits tornam colisão irrelevante para o volume de um jornal pessoal. Alternativa: URL slugificada — longa e com caracteres problemáticos.
- **Validação levanta `ValueError`**: exceção padrão; o adapter decide se descarta o item ou falha.
- **URL validada com `urllib.parse.urlsplit`**: exige scheme `http`/`https` e `netloc` não vazio. Sem regex.
- **Ports como `typing.Protocol` + `@runtime_checkable`**: tipagem estrutural, adapters não precisam herdar de nada. Alternativa ABC: força herança e importação do core em todo adapter sem ganho.
- **Checagem de fronteira por AST em teste**: `tests/test_core_boundary.py` percorre `domain/` e `ports/`, coleta imports e compara com `sys.stdlib_module_names` + prefixos `journal.domain`/`journal.ports`. A função de checagem recebe código-fonte, então o cenário de violação é testado com um trecho sintético. Alternativa `import-linter`: dependência extra para uma regra de ~20 linhas.

## Risks / Trade-offs

- [Mudança na normalização da URL (ex.: tracking params) muda o id] → Aceito: limpeza de URL, se vier, entra no adapter antes de criar o `Article`.
- [`runtime_checkable` só checa a existência do método, não a assinatura] → Suficiente para o cenário da spec; tipagem estática fica para quando houver type checker.
