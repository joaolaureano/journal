from typing import Protocol, runtime_checkable

from journal.domain import Story, StoryText


@runtime_checkable
class WriterPort(Protocol):
    """Writes one story from its items. Item text is data, never instructions."""

    def write(self, story: Story) -> StoryText | None:
        """The story's text, citing only its own items, or None.

        Called from several threads at once; may raise on failure."""
        ...
