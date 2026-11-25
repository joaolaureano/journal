"""Stands in for an installed plugin package in config tests."""

from fakes import FakeSource, article

from journal.config import AdapterType

FAKE = AdapterType(
    build=lambda options, _dir: FakeSource([article(options["url"])]),
    required={"url": str},
)
NOT_AN_ADAPTER = object()
