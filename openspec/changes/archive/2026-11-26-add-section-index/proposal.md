# Proposal

## Why

A edição tem várias seções (Ciência, Brasil e mundo, Tecnologia…) e, para chegar à última, é preciso rolar a página inteira. O João quer um índice logo abaixo de "Edição de …" que leve direto a cada seção.

## What Changes

- Em edições com seções, uma linha de links logo abaixo da data da edição, um por seção, na ordem da página, cada um levando ao título da seção (âncora na mesma página, sem scripts).
- Cada título de seção ganha um `id` derivado do nome: minúsculas, sem acentos, palavras unidas por hífen (`Brasil e mundo` → `brasil-e-mundo`).
- Edições sem seções não mostram índice.

## Impact

- `src/journal/adapters/static_site.py`, `templates/index.html`, `templates/style.css`, `tests/test_static_site.py`, spec `static-site`.
