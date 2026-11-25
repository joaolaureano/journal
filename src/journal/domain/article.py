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
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("article title must not be blank")
        parts = urlsplit(self.url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise ValueError(f"article url must be absolute http(s): {self.url!r}")
        if self.published_at.utcoffset() is None:
            raise ValueError("article published_at must be timezone-aware")
        object.__setattr__(
            self, "id", hashlib.sha256(self.url.encode()).hexdigest()[:16]
        )
