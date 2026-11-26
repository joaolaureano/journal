from dataclasses import replace

from journal.domain import Article
from journal.ports import SourcePort


class Sectioned:
    """Wraps any source so its articles belong to `section` and have `kind`."""

    def __init__(
        self, source: SourcePort, section: str | None = None, kind: str | None = None
    ):
        self.source = source
        self.section = section
        self.kind = kind
        self.name = getattr(source, "name", type(source).__name__)

    def fetch(self) -> list[Article]:
        stamp = {"section": self.section, "kind": self.kind}
        stamp = {k: v for k, v in stamp.items() if v is not None}
        return [replace(a, **stamp) for a in self.source.fetch()]
