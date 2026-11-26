from collections.abc import Sequence
from dataclasses import dataclass, field

from journal.app.filter import KeywordFilter
from journal.domain import Article
from journal.ports import PublisherPort, SourceError, SourcePort


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    articles: list[Article]
    errors: list[SourceError] = field(default_factory=list)
    fetched: int = 0  # unique articles read, before filtering


class BuildJournal:
    def __init__(
        self,
        sources: Sequence[SourcePort],
        publisher: PublisherPort,
        article_filter: KeywordFilter | None = None,
        max_articles: int | None = None,
    ):
        self.sources = sources
        self.publisher = publisher
        self.article_filter = article_filter
        self.max_articles = max_articles

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
            succeeded += 1
            for article in fetched:
                by_url.setdefault(article.url, article)
        if not succeeded:
            raise BuildError(
                "no source fetched successfully: "
                + ("; ".join(map(str, errors)) or "no sources configured")
            )
        kept = [
            a
            for a in by_url.values()
            if not self.article_filter or self.article_filter.matches(a)
        ]
        articles = sorted(kept, key=lambda a: (-a.published_at.timestamp(), a.url))
        articles = articles[: self.max_articles]
        self.publisher.publish(articles)
        return BuildReport(articles, errors, fetched=len(by_url))
