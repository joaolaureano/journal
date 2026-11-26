#!/usr/bin/env bash
# Empacota o journal para a Lambda em build/: código, journal.toml e dependências.
# Todas as dependências são Python puro, então o pacote serve para arm64 e x86_64.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf build
mkdir -p build
uv export --frozen --no-dev --no-hashes --no-emit-project -o build/requirements.txt >/dev/null
uv pip install --quiet --target build -r build/requirements.txt
cp -r src/journal build/journal
cp journal.toml build/journal.toml
find build -name __pycache__ -type d -prune -exec rm -rf {} +
echo "pacote pronto em build/ ($(du -sh build | cut -f1))"
