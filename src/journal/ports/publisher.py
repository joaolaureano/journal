from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from journal.domain import Article


@runtime_checkable
class PublisherPort(Protocol):
    def publish(self, articles: Sequence[Article]) -> None: ...


class PublishError(Exception):
    """A publisher could not publish the articles."""
