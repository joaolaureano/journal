from collections.abc import Sequence
from datetime import UTC, datetime

from journal.domain import Article


def article(url: str = "https://example.com/a", **overrides) -> Article:
    values = {
        "title": "Title",
        "summary": "",
        "source": "fake",
        "published_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    return Article(url=url, **(values | overrides))


class FakeSource:
    def __init__(self, articles: list[Article]):
        self.articles = articles

    def fetch(self) -> list[Article]:
        return list(self.articles)


class FakePublisher:
    def __init__(self):
        self.published: list[Article] = []

    def publish(self, articles: Sequence[Article]) -> None:
        self.published = list(articles)
