from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta, tzinfo

from journal.app.filter import KeywordFilter
from journal.domain import Article, Edition, dedup_key
from journal.ports import (
    HistoryPort,
    PublisherPort,
    SourceError,
    SourcePort,
    SummarizerPort,
)

__all__ = ["BuildError", "BuildJournal", "BuildReport", "dedup_key"]

FUTURE_TOLERANCE = timedelta(days=1)
WARMUP_WORKERS = 8
WARMUP_TIMEOUT = 180.0  # seconds for the whole step; the Lambda has 600


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    edition: Edition
    errors: list[SourceError] = field(default_factory=list)
    fetched: int = 0  # unique articles read, before filtering
    already_published: int = 0  # dropped: published in an earlier day's edition
    warmup_errors: list[str] = field(default_factory=list)  # distinct messages

    @property
    def warmups(self) -> int:
        return sum(a.warmup is not None for a in self.edition.articles)

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
        max_per_section: int | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
        timezone: tzinfo = UTC,
        history: HistoryPort | None = None,
        summarizer: SummarizerPort | None = None,
        warmup_timeout: float = WARMUP_TIMEOUT,
    ):
        self.sources = sources
        self.publisher = publisher
        self.article_filter = article_filter
        self.max_articles = max_articles
        self.max_age_days = max_age_days
        self.max_per_section = max_per_section
        self.now = now
        self.timezone = timezone  # decides which day an edition belongs to
        self.history = history  # what earlier editions already published
        self.summarizer = summarizer  # writes the articles' warm-up paragraph
        self.warmup_timeout = warmup_timeout

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
        if self.max_per_section is not None:
            articles = _cap_per_section(articles, self.max_per_section)
        articles = articles[: self.max_articles]
        # sections in the order their first source was configured; others last
        order = list(dict.fromkeys(getattr(s, "section", None) for s in self.sources))
        rank = {name: i for i, name in enumerate(n for n in order if n is not None)}
        articles.sort(key=lambda a: rank.get(a.section, len(rank)))  # stable
        articles, warmup_errors = self._warm_up(articles)
        edition = Edition(day, tuple(articles), self.timezone)
        self.publisher.publish(edition)
        return BuildReport(
            edition,
            errors,
            fetched=len(by_url),
            already_published=len(by_url) - len(fresh),
            warmup_errors=warmup_errors,
        )

    def _warm_up(self, articles: list[Article]) -> tuple[list[Article], list[str]]:
        """Adds the summarizer's warm-up to each `artigo`; failures only skip it."""
        targets = [a for a in articles if a.kind == "artigo"]
        if self.summarizer is None or not targets:
            return articles, []
        pool = ThreadPoolExecutor(WARMUP_WORKERS)
        futures = {pool.submit(self.summarizer.warmup, a): a for a in targets}
        done, pending = wait(futures, timeout=self.warmup_timeout)
        pool.shutdown(wait=False, cancel_futures=True)  # late calls are dropped
        texts, errors = {}, []
        for future in done:
            try:
                text = future.result()
            except Exception as exc:  # any adapter failure only skips this item
                errors.append(str(exc) or repr(exc))
                continue
            if text:
                texts[futures[future].key] = text
        if pending:
            errors.append(f"warm-up timed out: {len(pending)} articles without it")
        warmed = [
            replace(a, warmup=texts[a.key]) if a.key in texts else a for a in articles
        ]
        return warmed, list(dict.fromkeys(errors))

    def _in_window(self, article: Article) -> bool:
        """Drops stale articles and ones dated implausibly far in the future."""
        now = self.now()
        if article.published_at > now + FUTURE_TOLERANCE:
            return False
        if self.max_age_days is None or article.evergreen:
            return True
        return article.published_at >= now - timedelta(days=self.max_age_days)


def _cap_per_section(articles: list[Article], limit: int) -> list[Article]:
    """Keeps the first `limit` articles of each section and kind, preserving order."""
    counts: dict[tuple[str | None, str], int] = {}
    kept = []
    for a in articles:
        key = (a.section, a.kind)  # news and articles of a section count apart
        counts[key] = counts.get(key, 0) + 1
        if counts[key] <= limit:
            kept.append(a)
    return kept
