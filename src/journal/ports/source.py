from typing import Protocol, runtime_checkable

from journal.domain import Article


@runtime_checkable
class SourcePort(Protocol):
    def fetch(self) -> list[Article]: ...


class SourceError(Exception):
    """A source could not deliver its articles."""
