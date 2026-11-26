import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlsplit


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
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("article title must not be blank")
        if not is_http_url(self.url):
            raise ValueError(f"article url must be absolute http(s): {self.url!r}")
        if self.image is not None and not is_http_url(self.image):
            raise ValueError(f"article image must be absolute http(s): {self.image!r}")
        if self.published_at.utcoffset() is None:
            raise ValueError("article published_at must be timezone-aware")
        object.__setattr__(
            self, "id", hashlib.sha256(self.url.encode()).hexdigest()[:16]
        )


def is_http_url(value: str) -> bool:
    parts = urlsplit(value)
    return parts.scheme in ("http", "https") and bool(parts.netloc)
