"""One post a day from the archive of a paginated feed (WordPress: `?paged=N`).

Made for blogs that stopped but keep a valuable archive, such as The Morning
Paper: each edition gets one classic, and the same day always gets the same one.
"""

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, date, datetime
from urllib.parse import urlsplit, urlunsplit

from journal.adapters.rss import RssSource
from journal.domain import Article
from journal.ports import SourceError


class ArchiveSource:
    def __init__(
        self,
        location: str,
        name: str,
        pages: int,
        timeout: float = 10,
        # shortcut: UTC date, the same as São Paulo's at the 08:00 edition; pass the
        # edition's timezone if the schedule moves close to midnight.
        today: Callable[[], date] = lambda: datetime.now(UTC).date(),
        read: Callable[[str], list[Article]] | None = None,
    ):
        if pages < 1:
            raise ValueError("an archive needs at least one page")
        self.location = location
        self.name = name
        self.pages = pages
        self.today = today
        self.read = read or (
            lambda url: RssSource(url, name, timeout, full_text=True).fetch()
        )

    def fetch(self) -> list[Article]:
        # consecutive days walk consecutive pages; a page comes back only after
        # `pages` days, then with its next post
        n = self.today().toordinal()
        url = page_url(self.location, n % self.pages + 1)
        posts = self.read(url)
        if not posts:
            raise SourceError(f"archive page {url} has no valid entry")
        return [replace(posts[(n // self.pages) % len(posts)], evergreen=True)]


def page_url(location: str, page: int) -> str:
    """`location` with `paged=<page>` added to its query."""
    parts = urlsplit(location)
    query = f"{parts.query}&paged={page}" if parts.query else f"paged={page}"
    return urlunsplit(parts._replace(query=query))
