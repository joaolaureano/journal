from collections.abc import Sequence
from dataclasses import dataclass, field

from journal.domain import Article
from journal.ports import PublisherPort, SourceError, SourcePort


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    articles: list[Article]
    errors: list[SourceError] = field(default_factory=list)


class BuildJournal:
    def __init__(self, sources: Sequence[SourcePort], publisher: PublisherPort):
        self.sources = sources
        self.publisher = publisher

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
        articles = sorted(
            by_url.values(), key=lambda a: (-a.published_at.timestamp(), a.url)
        )
        self.publisher.publish(articles)
        return BuildReport(articles, errors)
