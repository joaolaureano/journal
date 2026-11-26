from datetime import date
from typing import Protocol, runtime_checkable


@runtime_checkable
class HistoryPort(Protocol):
    """What earlier editions published, so a story is not repeated on later days."""

    def published_before(self, day: date) -> set[str]:
        """Keys (`Article.key`) first published in an edition dated before `day`."""
        ...
