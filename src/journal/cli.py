"""Command-line entry point: the composition root wiring adapters into use cases."""

import argparse
import os
import sys

from journal.adapters.deepseek import DeepSeekSummarizer
from journal.app import BuildError, BuildJournal, BuildReport
from journal.app.build import WARMUP_TIMEOUT
from journal.config import Config, ConfigError, load_config
from journal.ports import HistoryPort, PublishError, SummarizerPort


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="journal")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="fetch sources and publish the site")
    build.add_argument(
        "--config", default="journal.toml", help="config file (default: journal.toml)"
    )
    args = parser.parse_args(argv)

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


def run(config: Config) -> BuildReport:
    """One build with everything the configuration declares."""
    publisher = config.publisher
    options = dict(config.summarizer or {})
    timeout = options.pop("timeout", WARMUP_TIMEOUT)
    return BuildJournal(
        config.sources,
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
