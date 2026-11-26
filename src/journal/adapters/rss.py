import http.client
import logging
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser

import feedparser

from journal.domain import Article, is_http_url
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
        # HTTPException covers IncompleteRead: the server cut the transfer midway.
        except (OSError, ValueError, http.client.HTTPException) as exc:
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
        image = _image(entry)
        caption = credit = None
        if image:
            caption = plain_text(entry.get("media_text", "")) or None
            credits = entry.get("media_credit") or [{}]
            credit = credits[0].get("content", "").strip() or None
        return Article(
            title=entry["title"],
            url=entry["link"],
            summary=plain_text(entry.get("summary", "")),
            source=self.name,
            published_at=datetime(*when[:6], tzinfo=UTC),
            image=image,
            image_caption=caption,
            image_credit=credit,
        )


def _image(entry) -> str | None:
    """First valid image URL from the entry's media fields, never from summary HTML."""
    candidates = [
        m.get("url")
        for m in entry.get("media_content", [])
        if m.get("medium") == "image"
        or (m.get("type") or "").startswith("image/")
        or not (m.get("medium") or m.get("type"))
    ]
    candidates += [t.get("url") for t in entry.get("media_thumbnail", [])]
    candidates += [
        e.get("href")
        for e in entry.get("enclosures", [])
        if (e.get("type") or "").startswith("image/")
    ]
    return next((u for u in candidates if u and is_http_url(u)), None)


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
