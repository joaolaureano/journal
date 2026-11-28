"""Command-line entry point: the composition root wiring adapters into use cases."""

import argparse
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field

from journal.adapters.deepseek import DeepSeekSummarizer
from journal.adapters.pool import Pooled
from journal.app import BuildError, BuildJournal, BuildReport, Sectioned
from journal.app.build import WARMUP_TIMEOUT
from journal.config import Config, ConfigError, load_config
from journal.ports import (
    HistoryPort,
    PublishError,
    SourceError,
    SourcePort,
    SummarizerPort,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="journal")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, text in (
        ("build", "fetch sources and publish the site"),
        ("collect", "fetch sources into the pool, without publishing"),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument(
            "--config",
            default="journal.toml",
            help="config file (default: journal.toml)",
        )
    args = parser.parse_args(argv)
    if args.command == "collect":
        return _collect_command(args.config)

    try:
        report = run(load_config(args.config))
    except (ConfigError, BuildError, PublishError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    for error in report.errors:
        print(f"source failed: {error}", file=sys.stderr)
    for error in report.warmup_errors:
        print(f"warm-up failed: {error}", file=sys.stderr)
    print(summary(report))
    return 0


def _collect_command(path: str) -> int:
    try:
        report = collect(load_config(path))
    except (ConfigError, BuildError) as exc:
        print(f"collect failed: {exc}", file=sys.stderr)
        return 1
    for error in report.errors:
        print(f"source failed: {error}", file=sys.stderr)
    print(
        f"collected {report.articles} articles from {report.succeeded}"
        f" of {report.sources} sources"
    )
    return 0


def run(config: Config) -> BuildReport:
    """One build with everything the configuration declares."""
    publisher = config.publisher
    options = dict(config.summarizer or {})
    timeout = options.pop("timeout", WARMUP_TIMEOUT)
    return BuildJournal(
        sources(config),
        publisher,
        config.article_filter,
        config.max_articles,
        config.max_age_days,
        config.max_per_section,
        timezone=config.timezone,
        history=publisher if isinstance(publisher, HistoryPort) else None,
        summarizer=summarizer(config, getattr(publisher, "storage", None)),
        warmup_timeout=timeout,
    ).run()


@dataclass
class CollectReport:
    sources: int  # configured
    succeeded: int = 0
    articles: int = 0  # available to the next edition: feed plus pool, after `paths`
    errors: list[SourceError] = field(default_factory=list)


def collect(config: Config) -> CollectReport:
    """Reads every source through the pool and stores it; publishes nothing."""
    if config.pool is None:
        raise ConfigError("[pool] is not configured, so there is nothing to collect")
    report = CollectReport(len(config.sources))
    for source in sources(config):
        try:
            report.articles += len(source.fetch())
        except SourceError as exc:
            report.errors.append(exc)
            continue
        except Exception as exc:  # a buggy adapter must not sink the others
            error = SourceError(f"unexpected error in source {source.name}: {exc!r}")
            error.__cause__ = exc
            report.errors.append(error)
            continue
        report.succeeded += 1
    if not report.succeeded:
        raise BuildError(
            "no source fetched successfully: "
            + ("; ".join(map(str, report.errors)) or "no sources configured")
        )
    return report


def sources(config: Config) -> list[SourcePort]:
    """The configured sources, read through the pool when [pool] is set."""
    if config.pool is None:
        return list(config.sources)
    storage = getattr(config.publisher, "storage", None)
    if storage is None:
        raise ConfigError("[pool] needs a publisher that has a storage")
    return pooled(config.sources, storage, config.pool)


def pooled(sources: Sequence[SourcePort], storage, hours: int) -> list[SourcePort]:
    """Pool inside `Sectioned`: `section`, `kind` and `paths` follow the config."""

    def wrap(source: SourcePort) -> SourcePort:
        if isinstance(source, Sectioned):
            inner = Pooled(source.source, storage, hours)
            return Sectioned(inner, source.section, source.kind, source.paths)
        return Pooled(source, storage, hours)

    return [wrap(s) for s in sources]


def summarizer(config: Config, cache=None) -> SummarizerPort | None:
    """DeepSeek when [summarizer] is configured and DEEPSEEK_API_KEY is set."""
    if config.summarizer is None:
        return None
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        print("warm-up skipped: DEEPSEEK_API_KEY is not set", file=sys.stderr)
        return None
    options = {k: v for k, v in config.summarizer.items() if k != "timeout"}
    return DeepSeekSummarizer(key, cache, **options)


def summary(report: BuildReport) -> str:
    return (
        f"published {len(report.articles)} of {report.fetched} articles"
        f" in the edition of {report.edition.date.isoformat()}"
        f" ({report.already_published} already in earlier editions,"
        f" {report.warmups} AI warm-ups)"
    )


if __name__ == "__main__":
    sys.exit(main())
