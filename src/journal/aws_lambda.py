"""AWS Lambda entry point: same build as `journal build`, publishing to S3.

The event `{"action": "collect"}` runs `journal collect` instead: it only fills
the pool and never reads the DeepSeek key.

Environment:
  JOURNAL_CONFIG   config file inside the package (default: journal.toml next to it)
  JOURNAL_BUCKET   if set, the static site goes to this bucket instead of the
                   storage declared in the config
  JOURNAL_PREFIX   optional key prefix inside the bucket
  JOURNAL_DEEPSEEK_KEY_PARAMETER
                   SSM SecureString holding the DeepSeek API key, read when
                   DEEPSEEK_API_KEY is unset; without a key there are no warm-ups
"""

import logging
import os
from pathlib import Path

from journal.adapters.s3 import S3Storage
from journal.adapters.static_site import StaticSitePublisher
from journal.cli import collect, run, summary
from journal.config import load_config

log = logging.getLogger("journal")
log.setLevel(logging.INFO)

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "journal.toml"


def handler(event, context, storage=None, ssm=None):
    """Runs one build or collection. Raises on failure so the scheduler sees it."""
    collecting = isinstance(event, dict) and event.get("action") == "collect"
    if not collecting:
        _load_deepseek_key(ssm)
    config = load_config(os.environ.get("JOURNAL_CONFIG", DEFAULT_CONFIG))
    bucket = os.environ.get("JOURNAL_BUCKET")
    if storage is None and bucket:
        storage = S3Storage(bucket, os.environ.get("JOURNAL_PREFIX", ""))
    if storage is not None:
        config.publisher = StaticSitePublisher(storage)
    if collecting:
        collected = collect(config)
        for error in collected.errors:
            log.warning("source failed: %s", error)
        log.info(
            "collected %d articles from %d of %d sources",
            collected.articles,
            collected.succeeded,
            collected.sources,
        )
        return {
            "collected": collected.articles,
            "sources": collected.sources,
            "source_errors": [str(e) for e in collected.errors],
        }
    report = run(config)
    for error in report.errors:
        log.warning("source failed: %s", error)
    for error in report.warmup_errors:
        log.warning("warm-up failed: %s", error)
    log.info(summary(report))
    return {
        "edition": report.edition.date.isoformat(),
        "published": len(report.articles),
        "fetched": report.fetched,
        "already_published": report.already_published,
        "warmups": report.warmups,
        "source_errors": [str(e) for e in report.errors],
    }


def _load_deepseek_key(ssm=None) -> None:
    """Puts the key from SSM in DEEPSEEK_API_KEY; a failure only costs the warm-ups."""
    name = os.environ.get("JOURNAL_DEEPSEEK_KEY_PARAMETER")
    if not name or os.environ.get("DEEPSEEK_API_KEY"):
        return
    try:
        if ssm is None:
            import boto3  # in the Lambda runtime

            ssm = boto3.client("ssm")
        value = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
    except Exception as exc:  # missing parameter, no permission, no boto3
        log.warning("warm-up key not read from %s: %s", name, exc)
        return
    os.environ["DEEPSEEK_API_KEY"] = value
