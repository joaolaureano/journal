import http.client
import logging
import re
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser

import feedparser

from journal.domain import Article, is_http_url
from journal.ports import SourceError

log = logging.getLogger(__name__)

SUMMARY_LIMIT = 400  # characters; feeds that ship the whole text are cut here
RETRY_STATUSES = {408, 429}  # plus every 5xx; other 4xx answers are final
# Footer WordPress appends to every summary: "O post X apareceu primeiro em Y."
WORDPRESS_FOOTER = re.compile(
    r"\s*(?:O post .+ apareceu primeiro em|The post .+ appeared first on) .+?\.?\s*$"
)


class _Transient(Exception):
    """A failure worth another attempt; becomes a SourceError when attempts run out."""


class RssSource:
    """Reads one RSS/Atom feed from any URL urllib opens (http, https, file)."""

    def __init__(
        self,
        location: str,
        name: str,
        timeout: float = 10,
        retries: int = 2,
        backoff: float = 1,
    ):
        self.location = location
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

    def fetch(self) -> list[Article]:
        for attempt in range(self.retries + 1):
            try:
                parsed = self._fetch_feed()
                break
            except _Transient as exc:
                if attempt == self.retries:
                    raise SourceError(str(exc)) from exc.__cause__
                delay = self.backoff * 2**attempt
                log.info("retrying %s in %ss: %s", self.location, delay, exc)
                time.sleep(delay)
        articles = []
        for entry in parsed.entries:
            try:
                articles.append(self._to_article(entry))
            except KeyError as exc:
                log.warning("skipping entry from %s: missing %s", self.location, exc)
            except ValueError as exc:
                log.warning("skipping entry from %s: %s", self.location, exc)
        return articles

    def _fetch_feed(self):
        request = urllib.request.Request(
            self.location, headers={"User-Agent": "journal/0.1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                content = response.read()
        except urllib.error.HTTPError as exc:
            message = f"cannot fetch feed {self.location}: {exc}"
            if exc.code >= 500 or exc.code in RETRY_STATUSES:
                raise _Transient(message) from exc
            raise SourceError(message) from exc
        # HTTPException covers IncompleteRead: the server cut the transfer midway.
        except (OSError, http.client.HTTPException) as exc:
            raise _Transient(f"cannot fetch feed {self.location}: {exc}") from exc
        except ValueError as exc:  # malformed URL: retrying cannot help
            raise SourceError(f"cannot fetch feed {self.location}: {exc}") from exc
        parsed = feedparser.parse(content)
        if not parsed.version:  # sometimes a half-written file on the server
            raise _Transient(f"not an RSS/Atom feed: {self.location}")
        return parsed

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
            summary=summary_text(entry.get("summary", "")),
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
    # last resort: first image of the full text (content:encoded), never the summary
    candidates += [_first_img(c.get("value", "")) for c in entry.get("content", [])]
    return next((u for u in candidates if u and is_http_url(u)), None)


class _ImgFinder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.src: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "img" and self.src is None:
            self.src = dict(attrs).get("src")


def _first_img(html: str) -> str | None:
    finder = _ImgFinder()
    finder.feed(html)
    finder.close()
    return finder.src


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


def summary_text(html: str) -> str:
    """Plain text without the WordPress footer, cut at a word near SUMMARY_LIMIT."""
    text = WORDPRESS_FOOTER.sub("", plain_text(html))
    if len(text) <= SUMMARY_LIMIT:
        return text
    cut = text[:SUMMARY_LIMIT].rsplit(" ", 1)[0].rstrip(" ,;:.-")
    return cut + "…"
