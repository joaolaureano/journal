import logging
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser

import feedparser

from journal.domain import Article
from journal.ports import SourceError

log = logging.getLogger(__name__)


class RssSource:
    """Reads one RSS/Atom feed from any URL urllib opens (http, https, file)."""

    def __init__(self, location: str, name: str, timeout: float = 10):
        self.location = location
        self.name = name
        self.timeout = timeout

    def fetch(self) -> list[Article]:
        request = urllib.request.Request(
            self.location, headers={"User-Agent": "journal/0.1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                content = response.read()
        except (OSError, ValueError) as exc:
            raise SourceError(f"cannot fetch feed {self.location}: {exc}") from exc
        parsed = feedparser.parse(content)
        if not parsed.version:
            raise SourceError(f"not an RSS/Atom feed: {self.location}")
        articles = []
        for entry in parsed.entries:
            try:
                articles.append(self._to_article(entry))
            except KeyError as exc:
                log.warning("skipping entry from %s: missing %s", self.location, exc)
            except ValueError as exc:
                log.warning("skipping entry from %s: %s", self.location, exc)
        return articles

    def _to_article(self, entry) -> Article:
        when = entry.get("published_parsed") or entry.get("updated_parsed")
        if when is None:
            raise ValueError(f"entry has no date: {entry.get('title')!r}")
        return Article(
            title=entry["title"],
            url=entry["link"],
            summary=plain_text(entry.get("summary", "")),
            source=self.name,
            published_at=datetime(*when[:6], tzinfo=UTC),
        )


class _TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def plain_text(html: str) -> str:
    collector = _TextCollector()
    collector.feed(html)
    collector.close()
    return " ".join(" ".join(collector.parts).split())
