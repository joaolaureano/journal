"""Keeps what each feed showed in earlier fetches, so an edition sees the whole day.

A feed lists only its latest items (some cover ~1.5 h), so an hourly collection
stores them and the edition reads them back.
"""

import hashlib
import json
import logging
from collections.abc import Callable
from dataclasses import fields
from datetime import UTC, datetime, timedelta

from journal.adapters.storage import StoragePort
from journal.domain import Article
from journal.ports import SourceError, SourcePort

log = logging.getLogger("journal")

PREFIX = "pool/"
MAX_ITEMS = 1000  # newest kept per source; bounds the file of a very busy feed
FIELDS = tuple(f.name for f in fields(Article) if f.init)


class Pooled:
    """A source that returns its feed plus what it stored in the last `hours` hours."""

    def __init__(
        self,
        source: SourcePort,
        storage: StoragePort,
        hours: int = 48,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self.source = source
        self.storage = storage
        self.hours = hours
        self.now = now
        self.name = getattr(source, "name", type(source).__name__)
        digest = hashlib.sha256(self.name.encode()).hexdigest()[:16]
        self.key = f"{PREFIX}{digest}.json"

    def fetch(self) -> list[Article]:
        # shortcut: a failed feed raises and its stored items miss this edition;
        # return them with a per-source warning once the build report has one.
        fresh = self.source.fetch()
        try:
            raw = self.storage.read(self.key)
        except Exception as exc:  # never overwrite a pool that could not be read
            raise SourceError(f"pool of {self.name} could not be read: {exc}") from exc
        merged = {a.key: a for a in self._load(raw)}
        merged.update((a.key, a) for a in fresh)  # the feed's version wins
        since = self.now() - timedelta(hours=self.hours)
        kept = sorted(
            (a for a in merged.values() if a.published_at >= since),
            key=lambda a: (-a.published_at.timestamp(), a.url),
        )[:MAX_ITEMS]
        try:
            self.storage.write(self.key, self._dump(kept))
        except Exception as exc:
            raise SourceError(f"pool of {self.name} could not be saved: {exc}") from exc
        in_feed = {a.key for a in fresh}
        return fresh + [a for a in kept if a.key not in in_feed]

    def _load(self, raw: bytes | None) -> list[Article]:
        """Stored articles; a missing, invalid or foreign entry counts as empty."""
        if raw is None:
            return []
        try:
            data = json.loads(raw)
            if data["source"] != self.name:
                raise ValueError(f"entry belongs to {data['source']!r}")
            items = list(data["articles"])
        except (ValueError, TypeError, KeyError) as exc:
            log.warning("pool of %s ignored: %s", self.name, exc)
            return []
        articles = []
        for item in items:
            try:
                values = {k: item[k] for k in FIELDS if k in item}
                values["published_at"] = datetime.fromisoformat(values["published_at"])
                articles.append(Article(**values))
            except (ValueError, TypeError, KeyError):
                continue  # one bad item does not spoil the rest
        return articles

    def _dump(self, articles: list[Article]) -> bytes:
        items = [
            {k: getattr(a, k) for k in FIELDS}
            | {"published_at": a.published_at.isoformat()}
            for a in articles
        ]
        data = {"source": self.name, "articles": items}
        return json.dumps(data, ensure_ascii=False).encode()
