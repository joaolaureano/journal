"""AWS Lambda entry point: same build as `journal build`, publishing to S3.

Environment:
  JOURNAL_CONFIG   config file inside the package (default: journal.toml next to it)
  JOURNAL_BUCKET   if set, the static site goes to this bucket instead of the
                   storage declared in the config
  JOURNAL_PREFIX   optional key prefix inside the bucket
"""

import logging
import os
from pathlib import Path

from journal.adapters.s3 import S3Storage
from journal.adapters.static_site import StaticSitePublisher
from journal.cli import run, summary
from journal.config import load_config

log = logging.getLogger("journal")
log.setLevel(logging.INFO)

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "journal.toml"


def handler(event, context, storage=None):
    """Runs one build. Raises on failure so Lambda and the scheduler see it failed."""
    config = load_config(os.environ.get("JOURNAL_CONFIG", DEFAULT_CONFIG))
    bucket = os.environ.get("JOURNAL_BUCKET")
    if storage is None and bucket:
        storage = S3Storage(bucket, os.environ.get("JOURNAL_PREFIX", ""))
    if storage is not None:
        config.publisher = StaticSitePublisher(storage)
    report = run(config)
    for error in report.errors:
        log.warning("source failed: %s", error)
    log.info(summary(report))
    return {
        "edition": report.edition.date.isoformat(),
        "published": len(report.articles),
        "fetched": report.fetched,
        "already_published": report.already_published,
        "source_errors": [str(e) for e in report.errors],
    }
