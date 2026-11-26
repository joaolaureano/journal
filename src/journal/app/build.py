from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, tzinfo
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from journal.app.filter import KeywordFilter
from journal.domain import Article, Edition
from journal.ports import PublisherPort, SourceError, SourcePort

FUTURE_TOLERANCE = timedelta(days=1)
TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


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


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    edition: Edition
    errors: list[SourceError] = field(default_factory=list)
    fetched: int = 0  # unique articles read, before filtering

    @property
    def articles(self) -> list[Article]:
        return list(self.edition.articles)


class BuildJournal:
    def __init__(
        self,
        sources: Sequence[SourcePort],
        publisher: PublisherPort,
        article_filter: KeywordFilter | None = None,
        max_articles: int | None = None,
        max_age_days: int | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
        timezone: tzinfo = UTC,
    ):
        self.sources = sources
        self.publisher = publisher
        self.article_filter = article_filter
        self.max_articles = max_articles
        self.max_age_days = max_age_days
        self.now = now
        self.timezone = timezone  # decides which day an edition belongs to

    def run(self) -> BuildReport:
        by_url: dict[str, Article] = {}
        errors: list[SourceError] = []
        succeeded = 0
        for source in self.sources:
            try:
                fetched = source.fetch()
            except SourceError as exc:
                errors.append(exc)
                continue
            except Exception as exc:  # a buggy adapter must not sink the others
                name = getattr(source, "name", type(source).__name__)
                error = SourceError(f"unexpected error in source {name}: {exc!r}")
                error.__cause__ = exc
                errors.append(error)
                continue
            succeeded += 1
            for article in fetched:
                by_url.setdefault(dedup_key(article.url), article)
        if not succeeded:
            raise BuildError(
                "no source fetched successfully: "
                + ("; ".join(map(str, errors)) or "no sources configured")
            )
        kept = [
            a
            for a in by_url.values()
            if self._in_window(a)
            and (not self.article_filter or self.article_filter.matches(a))
        ]
        articles = sorted(kept, key=lambda a: (-a.published_at.timestamp(), a.url))
        articles = articles[: self.max_articles]
        edition = Edition(self.now().astimezone(self.timezone).date(), tuple(articles))
        self.publisher.publish(edition)
        return BuildReport(edition, errors, fetched=len(by_url))

    def _in_window(self, article: Article) -> bool:
        """Drops stale articles and ones dated implausibly far in the future."""
        now = self.now()
        if article.published_at > now + FUTURE_TOLERANCE:
            return False
        if self.max_age_days is None:
            return True
        return article.published_at >= now - timedelta(days=self.max_age_days)
