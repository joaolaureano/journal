from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, tzinfo

from journal.app.filter import KeywordFilter
from journal.domain import Article, Edition, dedup_key
from journal.ports import HistoryPort, PublisherPort, SourceError, SourcePort

__all__ = ["BuildError", "BuildJournal", "BuildReport", "dedup_key"]

FUTURE_TOLERANCE = timedelta(days=1)


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    edition: Edition
    errors: list[SourceError] = field(default_factory=list)
    fetched: int = 0  # unique articles read, before filtering
    already_published: int = 0  # dropped: published in an earlier day's edition

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
        history: HistoryPort | None = None,
    ):
        self.sources = sources
        self.publisher = publisher
        self.article_filter = article_filter
        self.max_articles = max_articles
        self.max_age_days = max_age_days
        self.now = now
        self.timezone = timezone  # decides which day an edition belongs to
        self.history = history  # what earlier editions already published

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
                by_url.setdefault(article.key, article)
        if not succeeded:
            raise BuildError(
                "no source fetched successfully: "
                + ("; ".join(map(str, errors)) or "no sources configured")
            )
        day = self.now().astimezone(self.timezone).date()
        seen = self.history.published_before(day) if self.history else set()
        fresh = {k: a for k, a in by_url.items() if k not in seen}
        kept = [
            a
            for a in fresh.values()
            if self._in_window(a)
            and (not self.article_filter or self.article_filter.matches(a))
        ]
        articles = sorted(kept, key=lambda a: (-a.published_at.timestamp(), a.url))
        articles = articles[: self.max_articles]
        edition = Edition(day, tuple(articles))
        self.publisher.publish(edition)
        return BuildReport(
            edition,
            errors,
            fetched=len(by_url),
            already_published=len(by_url) - len(fresh),
        )

    def _in_window(self, article: Article) -> bool:
        """Drops stale articles and ones dated implausibly far in the future."""
        now = self.now()
        if article.published_at > now + FUTURE_TOLERANCE:
            return False
        if self.max_age_days is None:
            return True
        return article.published_at >= now - timedelta(days=self.max_age_days)
