"""Builds sources and publisher from a TOML file via a registry of adapter types.

Outside the core on purpose: this is where concrete adapters are named.
"""

import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import tzinfo
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from journal.adapters.rss import RssSource
from journal.adapters.s3 import S3Storage
from journal.adapters.static_site import StaticSitePublisher
from journal.adapters.storage import LocalStorage
from journal.app import KeywordFilter, Sectioned
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
        build=lambda o, _dir: RssSource(o["url"], o["name"], _timeout(o)),
        required={"name": str, "url": str},
        optional={"timeout": (int, float)},
    ),
}


def _timeout(options: dict[str, Any]) -> float:
    timeout = options.get("timeout", 10)
    if timeout <= 0:
        raise ConfigError(f"source {options['name']!r} (rss): 'timeout' must be > 0")
    return timeout


STORAGE_TYPES: dict[str, AdapterType] = {
    "local": AdapterType(
        build=lambda o, config_dir: LocalStorage(config_dir / o.get("out", "dist")),
        optional={"out": str},
    ),
    "s3": AdapterType(
        build=lambda o, _dir: S3Storage(o["bucket"], o.get("prefix", "")),
        required={"bucket": str},
        optional={"prefix": str},
    ),
}


def _static_site(options: dict[str, Any], config_dir: Path) -> StaticSitePublisher:
    if "out" in options and "storage" in options:
        raise ConfigError("publisher (static-site): use either 'out' or 'storage'")
    storage = options.get(
        "storage", {"type": "local", "out": options.get("out", "dist")}
    )
    return StaticSitePublisher(
        _build(
            storage, STORAGE_TYPES, "journal.storages", "publisher storage", config_dir
        )
    )


PUBLISHER_TYPES: dict[str, AdapterType] = {
    "static-site": AdapterType(
        build=_static_site,
        optional={"out": str, "storage": dict},
    ),
}

DEFAULT_TIMEZONE = "America/Sao_Paulo"


@dataclass
class Config:
    sources: list[SourcePort]
    publisher: PublisherPort
    article_filter: KeywordFilter | None = None
    max_articles: int | None = None
    max_age_days: int | None = None
    max_per_section: int | None = None
    timezone: tzinfo = field(default_factory=lambda: ZoneInfo(DEFAULT_TIMEZONE))


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

    article_filter, limits = _filter(data.get("filter"), path)
    config_dir = path.resolve().parent
    timezone = _timezone(data.get("timezone", DEFAULT_TIMEZONE), path)
    return Config(
        sources=[
            _source(entry, f"source #{i}", config_dir)
            for i, entry in enumerate(sources, start=1)
        ],
        publisher=_build(
            publisher, PUBLISHER_TYPES, "journal.publishers", "publisher", config_dir
        ),
        article_filter=article_filter,
        **limits,
        timezone=timezone,
    )


def _timezone(name: Any, path: Path) -> tzinfo:
    """IANA name such as 'America/Sao_Paulo'; decides the date of each edition."""
    if not isinstance(name, str):
        raise ConfigError(f"{path}: 'timezone' must be a string")
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConfigError(f"{path}: unknown timezone {name!r}") from exc


def _source(entry: Any, where: str, config_dir: Path) -> SourcePort:
    """`section` is accepted on every source type and handled here, not by adapters."""
    if not isinstance(entry, dict) or "section" not in entry:
        return _build(entry, SOURCE_TYPES, "journal.sources", where, config_dir)
    options = dict(entry)
    section = options.pop("section")
    if not isinstance(section, str) or not section.strip():
        raise ConfigError(f"{where}: 'section' must be a non-empty string")
    source = _build(options, SOURCE_TYPES, "journal.sources", where, config_dir)
    return Sectioned(source, section.strip())


LIMITS = ("max_articles", "max_age_days", "max_per_section")


def _filter(table: Any, path: Path) -> tuple[KeywordFilter | None, dict[str, int]]:
    if table is None:
        return None, {}
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [filter] must be a table")
    if unknown := sorted(table.keys() - {"include", "exclude", *LIMITS}):
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
    for key in LIMITS:
        value = table.get(key)
        if value is None:
            continue
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigError(f"{path}: [filter] {key!r} must be a positive integer")
        limits[key] = value
    return KeywordFilter(**terms), limits


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
