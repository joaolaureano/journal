"""Command-line entry point: the composition root wiring adapters into use cases."""

import argparse
import sys

from journal.app import BuildError, BuildJournal
from journal.config import ConfigError, load_config
from journal.ports import PublishError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="journal")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="fetch sources and publish the site")
    build.add_argument(
        "--config", default="journal.toml", help="config file (default: journal.toml)"
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        report = BuildJournal(
            config.sources,
            config.publisher,
            config.article_filter,
            config.max_articles,
        ).run()
    except (ConfigError, BuildError, PublishError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    for error in report.errors:
        print(f"source failed: {error}", file=sys.stderr)
    print(f"published {len(report.articles)} of {report.fetched} articles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
