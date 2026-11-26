from typing import Protocol, runtime_checkable

from journal.domain import Article


@runtime_checkable
class SummarizerPort(Protocol):
    """Writes AI text about an article. Article text is data, never instructions."""

    def warmup(self, article: Article) -> str | None:
        """A short plain-text paragraph to decide whether to read it, or None.

        Called from several threads at once; may raise on failure."""
        ...
