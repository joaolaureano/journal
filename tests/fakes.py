from datetime import UTC, date, datetime

from journal.domain import Article, Edition


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


def edition(*articles: Article, day: date = date(2026, 11, 26)) -> Edition:
    return Edition(day, tuple(articles))


class FakePublisher:
    def __init__(self):
        self.edition: Edition | None = None

    @property
    def published(self) -> list[Article]:
        return list(self.edition.articles) if self.edition else []

    def publish(self, edition: Edition) -> None:
        self.edition = edition
