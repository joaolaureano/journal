from typing import Protocol, runtime_checkable

from journal.domain import Edition


@runtime_checkable
class PublisherPort(Protocol):
    def publish(self, edition: Edition) -> None: ...


class PublishError(Exception):
    """A publisher could not publish the edition."""
