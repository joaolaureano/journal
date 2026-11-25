import ast
import sys
from pathlib import Path

import journal

CORE_LAYERS = ("domain", "ports", "app")
ALLOWED_PREFIXES = tuple(f"journal.{layer}" for layer in CORE_LAYERS)


def forbidden_imports(source: str) -> list[str]:
    """Imports in `source` that are neither stdlib nor core layers."""
    names = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            # relative imports could reach adapters/app unseen; core uses absolute only
            names.append("." * node.level + (node.module or ""))
    return [
        name
        for name in names
        if name.split(".")[0] not in sys.stdlib_module_names
        and not any(name == p or name.startswith(p + ".") for p in ALLOWED_PREFIXES)
    ]


def test_core_layers_respect_boundary():
    root = Path(journal.__file__).parent
    violations = {
        str(path.relative_to(root)): found
        for layer in CORE_LAYERS
        for path in (root / layer).rglob("*.py")
        if (found := forbidden_imports(path.read_text()))
    }
    assert violations == {}


def test_boundary_violation_is_detected():
    source = (
        "import feedparser\n"
        "from journal.adapters import rss\n"
        "from ..adapters import x\n"
        "import journal.cli\n"
        "from datetime import UTC\n"
    )
    assert forbidden_imports(source) == [
        "feedparser",
        "journal.adapters",
        "..adapters",
        "journal.cli",
    ]
