from dataclasses import replace

from journal.domain import Article
from journal.ports import SourcePort


class Sectioned:
    """Wraps any source so its articles belong to `section`."""

    def __init__(self, source: SourcePort, section: str):
        self.source = source
        self.section = section
        self.name = getattr(source, "name", type(source).__name__)

    def fetch(self) -> list[Article]:
        return [replace(a, section=self.section) for a in self.source.fetch()]
