"""Builds sources and publisher from a TOML file via a registry of adapter types.

Outside the core on purpose: this is where concrete adapters are named.
"""

import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

from journal.adapters.rss import RssSource
from journal.adapters.static_site import StaticSitePublisher
from journal.app import KeywordFilter
from journal.ports import PublisherPort, SourcePort

OptionTypes = dict[str, type | tuple[type, ...]]


class ConfigError(Exception):
    """The configuration file is missing or invalid."""


@dataclass(frozen=True)
class AdapterType:
    build: Callable[[dict[str, Any], Path], Any]  # (validated options, config dir)
    required: OptionTypes = field(default_factory=dict)
    optional: OptionTypes = field(default_factory=dict)


SOURCE_TYPES: dict[str, AdapterType] = {
    "rss": AdapterType(
        build=lambda o, _dir: RssSource(o["url"], o["name"], o.get("timeout", 10)),
        required={"name": str, "url": str},
        optional={"timeout": (int, float)},
    ),
}

PUBLISHER_TYPES: dict[str, AdapterType] = {
    "static-site": AdapterType(
        build=lambda o, config_dir: StaticSitePublisher(
            config_dir / o.get("out", "dist")
        ),
        optional={"out": str},
    ),
}


@dataclass
class Config:
    sources: list[SourcePort]
    publisher: PublisherPort
    article_filter: KeywordFilter | None = None
    max_articles: int | None = None
    max_age_days: int | None = None


def load_config(path: str | Path) -> Config:
    path = Path(path)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ConfigError(f"{path}: at least one [[sources]] entry is required")
    publisher = data.get("publisher")
    if not isinstance(publisher, dict):
        raise ConfigError(f"{path}: a [publisher] table is required")

    article_filter, max_articles, max_age_days = _filter(data.get("filter"), path)
    config_dir = path.resolve().parent
    return Config(
        sources=[
            _build(entry, SOURCE_TYPES, "journal.sources", f"source #{i}", config_dir)
            for i, entry in enumerate(sources, start=1)
        ],
        publisher=_build(
            publisher, PUBLISHER_TYPES, "journal.publishers", "publisher", config_dir
        ),
        article_filter=article_filter,
        max_articles=max_articles,
        max_age_days=max_age_days,
    )


def _filter(
    table: Any, path: Path
) -> tuple[KeywordFilter | None, int | None, int | None]:
    if table is None:
        return None, None, None
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [filter] must be a table")
    if unknown := sorted(
        table.keys() - {"include", "exclude", "max_articles", "max_age_days"}
    ):
        raise ConfigError(f"{path}: [filter] unknown option {unknown[0]!r}")
    terms = {}
    for key in ("include", "exclude"):
        value = table.get(key, [])
        if not isinstance(value, list) or not all(
            isinstance(t, str) and t.strip() for t in value
        ):
            raise ConfigError(
                f"{path}: [filter] {key!r} must be a list of non-empty strings"
            )
        terms[key] = value
    limits = {}
    for key in ("max_articles", "max_age_days"):
        value = limits[key] = table.get(key)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 1
        ):
            raise ConfigError(f"{path}: [filter] {key!r} must be a positive integer")
    return KeywordFilter(**terms), limits["max_articles"], limits["max_age_days"]


def _build(
    entry: Any,
    registry: dict[str, AdapterType],
    group: str,
    where: str,
    config_dir: Path,
):
    if not isinstance(entry, dict):
        raise ConfigError(f"{where}: must be a table")
    options = dict(entry)
    kind = options.pop("type", None)
    if not isinstance(kind, str):
        raise ConfigError(f"{where}: 'type' must be a string")
    spec = _resolve(kind, registry, group, where)
    if missing := sorted(spec.required.keys() - options.keys()):
        names = ", ".join(map(repr, missing))
        raise ConfigError(f"{where} ({kind}): missing option {names}")
    expected = spec.required | spec.optional
    for name, value in options.items():
        if name not in expected:
            raise ConfigError(f"{where} ({kind}): unknown option {name!r}")
        wanted = expected[name]
        wanted = wanted if isinstance(wanted, tuple) else (wanted,)
        if not isinstance(value, wanted) or (
            isinstance(value, bool) and bool not in wanted
        ):
            names = " or ".join(t.__name__ for t in wanted)
            raise ConfigError(f"{where} ({kind}): option {name!r} must be {names}")
    return spec.build(options, config_dir)


def _resolve(
    kind: str, registry: dict[str, AdapterType], group: str, where: str
) -> AdapterType:
    """Built-in or plugin (entry point) type; plugins are imported only when used."""
    plugins = list(entry_points(group=group, name=kind))
    providers = (["built-in"] if kind in registry else []) + [p.value for p in plugins]
    if not providers:
        known = sorted(set(registry) | set(entry_points(group=group).names))
        raise ConfigError(f"{where}: unknown type {kind!r} (known: {', '.join(known)})")
    if len(providers) > 1:
        raise ConfigError(
            f"{where}: type {kind!r} is ambiguous, provided by: {', '.join(providers)}"
        )
    if not plugins:
        return registry[kind]
    plugin = plugins[0]
    try:
        spec = plugin.load()
    except Exception as exc:  # any import-time failure in third-party code
        raise ConfigError(
            f"{where}: cannot load plugin for type {kind!r} ({plugin.value}): {exc}"
        ) from exc
    if not isinstance(spec, AdapterType):
        raise ConfigError(
            f"{where}: plugin for type {kind!r} ({plugin.value}) is not an AdapterType"
        )
    return spec
