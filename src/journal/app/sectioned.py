from collections.abc import Sequence
from dataclasses import replace
from urllib.parse import urlsplit

from journal.domain import Article
from journal.ports import SourcePort


class Sectioned:
    """Wraps any source so its articles belong to `section` and have `kind`.

    With `paths`, only articles whose link path starts with one of them are kept,
    so one general feed can feed several sections.
    """

    def __init__(
        self,
        source: SourcePort,
        section: str | None = None,
        kind: str | None = None,
        paths: Sequence[str] | None = None,
    ):
        self.source = source
        self.section = section
        self.kind = kind
        self.paths = tuple(paths) if paths else None
        self.name = getattr(source, "name", type(source).__name__)

    def fetch(self) -> list[Article]:
        stamp = {"section": self.section, "kind": self.kind}
        stamp = {k: v for k, v in stamp.items() if v is not None}
        articles = self.source.fetch()
        if self.paths:
            articles = [
                a for a in articles if urlsplit(a.url).path.startswith(self.paths)
            ]
        return [replace(a, **stamp) for a in articles]
