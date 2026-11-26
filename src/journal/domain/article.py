import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
KINDS = ("noticia", "artigo")  # news to skim, articles to read calmly


@dataclass(frozen=True)
class Article:
    title: str
    url: str
    summary: str
    source: str
    published_at: datetime
    image: str | None = None
    image_caption: str | None = None
    image_credit: str | None = None
    section: str | None = None  # e.g. "Ciência"; set from the source's configuration
    body: str | None = None  # full text as safe HTML, already rebuilt by the source
    kind: str = "noticia"  # one of KINDS
    warmup: str | None = None  # AI-written plain-text teaser; see SummarizerPort
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("article title must not be blank")
        if not is_http_url(self.url):
            raise ValueError(f"article url must be absolute http(s): {self.url!r}")
        if self.image is not None and not is_http_url(self.image):
            raise ValueError(f"article image must be absolute http(s): {self.image!r}")
        if self.kind not in KINDS:
            raise ValueError(f"article kind must be one of {KINDS}: {self.kind!r}")
        if self.published_at.utcoffset() is None:
            raise ValueError("article published_at must be timezone-aware")
        object.__setattr__(
            self, "id", hashlib.sha256(self.url.encode()).hexdigest()[:16]
        )

    @property
    def key(self) -> str:
        """Identity of the story across sources and editions; see `dedup_key`."""
        return dedup_key(self.url)


def is_http_url(value: str) -> bool:
    parts = urlsplit(value)
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def dedup_key(url: str) -> str:
    """Same story, same key: ignores scheme, `www.`, fragment, tracking params
    and a trailing slash. 'http://www.a.com/x/?utm_source=y#z' -> 'a.com/x'."""
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    query = urlencode(
        [
            (k, v)
            for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in TRACKING_PARAMS
        ]
    )
    return urlunsplit(("", host, parts.path.rstrip("/"), query, "")).lstrip("/")
