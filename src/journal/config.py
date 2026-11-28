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

from journal.adapters.archive import ArchiveSource
from journal.adapters.rss import RssSource
from journal.adapters.s3 import S3Storage
from journal.adapters.static_site import StaticSitePublisher
from journal.adapters.storage import LocalStorage
from journal.app import KeywordFilter, Sectioned
from journal.domain import KINDS
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
        build=lambda o, _dir: RssSource(
            o["url"], o["name"], _timeout(o), full_text=o.get("full_text", False)
        ),
        required={"name": str, "url": str},
        optional={"timeout": (int, float), "full_text": bool},
    ),
    "rss-archive": AdapterType(
        build=lambda o, _dir: ArchiveSource(
            o["url"], o["name"], _pages(o), _timeout(o)
        ),
        required={"name": str, "url": str, "pages": int},
        optional={"timeout": (int, float)},
    ),
}


def _pages(options: dict[str, Any]) -> int:
    pages = options["pages"]
    if isinstance(pages, bool) or pages < 1:
        name = options["name"]
        raise ConfigError(f"source {name!r} (rss-archive): 'pages' must be positive")
    return pages


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
    summarizer: dict[str, Any] | None = None  # [summarizer] options; None: no AI text
    pool: int | None = None  # [pool] hours; None: sources read only from their feeds
    stories: dict[str, Any] | None = None  # [stories] options; None: no grouping


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
        summarizer=_summarizer(data.get("summarizer"), path),
        pool=_pool(data.get("pool"), path),
        stories=_stories(data.get("stories"), path),
    )


SUMMARIZER_OPTIONS: OptionTypes = {
    "model": str,
    "max_calls": int,
    "max_input_chars": int,
    "timeout": (int, float),
}


def _summarizer(table: Any, path: Path) -> dict[str, Any] | None:
    """Validated [summarizer] options; the adapter is built where the key is known."""
    if table is None:
        return None
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [summarizer] must be a table")
    for key, value in table.items():
        wanted = SUMMARIZER_OPTIONS.get(key)
        if wanted is None:
            raise ConfigError(f"{path}: [summarizer] unknown option {key!r}")
        if key == "model":
            valid = isinstance(value, str) and bool(value.strip())
        else:
            valid = (
                isinstance(value, wanted) and not isinstance(value, bool) and value > 0
            )
        if not valid:
            what = "a non-empty string" if key == "model" else "a positive number"
            raise ConfigError(f"{path}: [summarizer] {key!r} must be {what}")
    return dict(table)


STORIES_OPTIONS: OptionTypes = {
    "max_stories": int,
    "model": str,
    "timeout": (int, float),
    "max_calls": int,
    "max_input_chars": int,
}


def _stories(table: Any, path: Path) -> dict[str, Any] | None:
    """Validated [stories] options; the grouper is built where the key is known."""
    if table is None:
        return None
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [stories] must be a table")
    for key, value in table.items():
        wanted = STORIES_OPTIONS.get(key)
        if wanted is None:
            raise ConfigError(f"{path}: [stories] unknown option {key!r}")
        if key == "model":
            valid = isinstance(value, str) and bool(value.strip())
        else:
            valid = (
                isinstance(value, wanted) and not isinstance(value, bool) and value > 0
            )
        if not valid:
            what = "a non-empty string" if key == "model" else "a positive number"
            raise ConfigError(f"{path}: [stories] {key!r} must be {what}")
    return dict(table)


DEFAULT_POOL_HOURS = 48  # covers Saturday to Monday: there is no Sunday edition


def _pool(table: Any, path: Path) -> int | None:
    """Hours of earlier fetches kept per source, or None without a [pool] table."""
    if table is None:
        return None
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [pool] must be a table")
    for key in table:
        if key != "hours":
            raise ConfigError(f"{path}: [pool] unknown option {key!r}")
    hours = table.get("hours", DEFAULT_POOL_HOURS)
    if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
        raise ConfigError(f"{path}: [pool] 'hours' must be a positive integer")
    return hours


def _timezone(name: Any, path: Path) -> tzinfo:
    """IANA name such as 'America/Sao_Paulo'; decides the date of each edition."""
    if not isinstance(name, str):
        raise ConfigError(f"{path}: 'timezone' must be a string")
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConfigError(f"{path}: unknown timezone {name!r}") from exc


def _source(entry: Any, where: str, config_dir: Path) -> SourcePort:
    """`section`, `kind` and `paths` work on every source type and are handled here."""
    if not isinstance(entry, dict) or not {"section", "kind", "paths"} & entry.keys():
        return _build(entry, SOURCE_TYPES, "journal.sources", where, config_dir)
    options = dict(entry)
    section = options.pop("section", None)
    if section is not None and (not isinstance(section, str) or not section.strip()):
        raise ConfigError(f"{where}: 'section' must be a non-empty string")
    kind = options.pop("kind", None)
    if kind is not None and kind not in KINDS:
        raise ConfigError(f"{where}: 'kind' must be one of {', '.join(KINDS)}")
    paths = options.pop("paths", None)
    if paths is not None and not (
        isinstance(paths, list)
        and paths
        and all(isinstance(p, str) and p.startswith("/") for p in paths)
    ):
        raise ConfigError(
            f"{where}: 'paths' must be a non-empty list of paths starting with /"
        )
    source = _build(options, SOURCE_TYPES, "journal.sources", where, config_dir)
    return Sectioned(source, section.strip() if section else None, kind, paths)


LIMITS = ("max_articles", "max_age_days", "max_per_section")
TERM_LISTS = ("include", "exclude", "exclude_domains")


def _filter(table: Any, path: Path) -> tuple[KeywordFilter | None, dict[str, int]]:
    if table is None:
        return None, {}
    if not isinstance(table, dict):
        raise ConfigError(f"{path}: [filter] must be a table")
    if unknown := sorted(table.keys() - {*TERM_LISTS, *LIMITS}):
        raise ConfigError(f"{path}: [filter] unknown option {unknown[0]!r}")
    terms = {}
    for key in TERM_LISTS:
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
