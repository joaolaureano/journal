import http.client
import logging
import re
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin

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
# What hnrss.org writes instead of a summary: links and counters, not text.
HNRSS_STATS = re.compile(
    r"(?:Article URL|Comments URL): \S+|Points: \d+|# Comments: \d+"
)

# Body allowlist: everything else is dropped (with its content) or unwrapped.
BODY_TAGS = {
    "p", "br", "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "b", "i", "sub", "sup", "figure", "figcaption", "a", "img",
}  # fmt: skip
BODY_RENAMED = {"h1": "h2", "h5": "h4", "h6": "h4"}  # the page's own h1 is the title
BODY_DROPPED = {
    "script", "style", "iframe", "object", "embed", "form", "svg", "video", "audio",
    "noscript", "template", "button", "select", "textarea",
}  # fmt: skip
VOID_TAGS = {"br", "img"}
# Months whose Portuguese abbreviation differs from the English one (UOL's dates).
PT_MONTHS = {"fev": "Feb", "abr": "Apr", "mai": "May", "ago": "Aug", "set": "Sep",
             "out": "Oct", "dez": "Dec"}  # fmt: skip
PIXEL_MAX = 2  # px; images this small are trackers


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
        full_text: bool = False,
    ):
        self.location = location
        self.full_text = full_text
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
        # dict.get skips feedparser's deprecated updated -> published fallback
        when = dict.get(entry, "published_parsed") or dict.get(entry, "updated_parsed")
        if when is not None:
            published_at = datetime(*when[:6], tzinfo=UTC)
        else:
            text = dict.get(entry, "published") or dict.get(entry, "updated")
            published_at = _rfc822_pt(text)
        if published_at is None:
            raise ValueError(f"entry has no date: {entry.get('title')!r}")
        image = _image(entry)
        caption = credit = None
        if image:
            caption = plain_text(entry.get("media_text", "")) or None
            credits = entry.get("media_credit") or [{}]
            credit = credits[0].get("content", "").strip() or None
        summary = summary_text(entry.get("summary", ""))
        return Article(
            title=entry["title"],
            url=entry["link"],
            summary=summary,
            source=self.name,
            published_at=published_at,
            image=image,
            image_caption=caption,
            image_credit=credit,
            body=self._body(entry, image, summary) if self.full_text else None,
        )

    def _body(self, entry, image: str | None, summary: str) -> str | None:
        """The entry's longest text as safe HTML, when it adds to the summary."""
        texts = [c.get("value", "") for c in entry.get("content", [])]
        texts.append(entry.get("summary", ""))
        bodies = [body_html(t, entry["link"], image) for t in texts]
        body = max(bodies, key=lambda b: len(plain_text(b)))
        if len(plain_text(body)) > len(summary) or "<img " in body:
            return body
        return None


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


def _rfc822_pt(text: str | None) -> datetime | None:
    """'Qui, 26 Nov 2026 10:08:44 -0300', the RFC 822 date in Portuguese feedparser
    leaves unparsed; None when it is not a date."""
    if not text:
        return None
    text = re.sub(r"^\s*[^\W\d_]+\.?,\s*", "", text)  # the weekday is redundant
    text = re.sub(r"[^\W\d_]{3}", lambda m: PT_MONTHS.get(m[0].lower(), m[0]), text)
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    return parsed.replace(tzinfo=parsed.tzinfo or UTC).astimezone(UTC)


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


class _BodyBuilder(HTMLParser):
    """Writes a new document from the allowlist; input markup is never copied."""

    def __init__(self, base_url: str, skip_src: str | None):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.skip_src = skip_src
        self.out: list[str] = []
        self.open: list[str] = []
        self._dropped = 0
        self._paragraph: tuple[int, int] | None = None  # (out index, open depth)

    def handle_starttag(self, tag, attrs):
        if tag in BODY_DROPPED:
            self._dropped += 1
        if self._dropped:
            return
        tag = BODY_RENAMED.get(tag, tag)
        if tag not in BODY_TAGS:
            return
        attrs = {k: v or "" for k, v in attrs}
        if tag == "img":
            self._img(attrs)
            return
        if tag == "br":
            self.out.append("<br>")
            return
        if tag == "a":
            href = self._url(attrs.get("href", ""))
            link = f' href="{escape(href)}"' if href else ""
            self.out.append(f'<a{link} rel="noopener noreferrer">')
        else:
            if tag == "p" and self._paragraph is None:
                self._paragraph = (len(self.out), len(self.open))
            self.out.append(f"<{tag}>")
        self.open.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in BODY_DROPPED:
            self._dropped = max(0, self._dropped - 1)
            return
        if self._dropped:
            return
        tag = BODY_RENAMED.get(tag, tag)
        if tag in VOID_TAGS or tag not in self.open:
            return  # stray end tags are ignored
        while self.open:
            closed = self.open.pop()
            self.out.append(f"</{closed}>")
            if (
                closed == "p"
                and self._paragraph
                and len(self.open) == self._paragraph[1]
            ):
                self._end_paragraph()
            if closed == tag:
                break

    def handle_data(self, data):
        if not self._dropped:
            self.out.append(escape(data, quote=False))

    def close(self):
        super().close()
        if self.open:  # unclosed tags must not leak into the page
            self.handle_endtag(self.open[0])

    def _end_paragraph(self):
        start, _ = self._paragraph
        self._paragraph = None
        if WORDPRESS_FOOTER.match(plain_text("".join(self.out[start:]))):
            del self.out[start:]

    def _img(self, attrs):
        src = attrs.get("src", "")
        if not is_http_url(urljoin(self.base_url, src)):  # e.g. data: placeholders
            src = attrs.get("data-src", src)  # lazy-loading WordPress themes
        src = self._url(src)
        if not src or src == self.skip_src:
            return
        for side in ("width", "height"):
            size = re.match(r"\s*(\d+)", attrs.get(side, ""))
            if size and int(size.group(1)) <= PIXEL_MAX:
                return
        alt = escape(attrs.get("alt", ""))
        self.out.append(
            f'<img src="{escape(src)}" alt="{alt}" loading="lazy"'
            ' referrerpolicy="no-referrer">'
        )

    def _url(self, value: str) -> str | None:
        url = urljoin(self.base_url, value.strip())
        return url if value.strip() and is_http_url(url) else None


def body_html(html: str, base_url: str, skip_src: str | None = None) -> str:
    """Feed HTML rebuilt through the allowlist, with links resolved to `base_url`."""
    breaks = re.compile(r"\s*(?:\n|<br\s*/?>)\s*", re.I)
    if not re.search(r"<p[\s>]", html, re.I) and breaks.search(html.strip()):
        lines = breaks.split(html)  # plain-text feeds: g1, Slashdot
        html = "".join(f"<p>{line}</p>" for line in lines if line.strip())
    builder = _BodyBuilder(base_url, skip_src)
    builder.feed(html)
    builder.close()
    return "".join(builder.out).strip()


def plain_text(html: str) -> str:
    collector = _TextCollector()
    collector.feed(html)
    collector.close()
    return " ".join(" ".join(collector.parts).split())


def summary_text(html: str) -> str:
    """Plain text without the WordPress footer, cut at a word near SUMMARY_LIMIT."""
    text = WORDPRESS_FOOTER.sub("", plain_text(html))
    if "Comments URL: " in text:  # hnrss.org
        text = " ".join(HNRSS_STATS.sub("", text).split())
    if text.casefold() == "comments":  # Hacker News and Lobsters: only a link
        return ""
    if len(text) <= SUMMARY_LIMIT:
        return text
    cut = text[:SUMMARY_LIMIT].rsplit(" ", 1)[0].rstrip(" ,;:.-")
    return cut + "…"
