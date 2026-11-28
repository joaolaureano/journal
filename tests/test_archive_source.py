from datetime import date, timedelta

import pytest
from fakes import article

from journal.adapters.archive import ArchiveSource, page_url
from journal.ports import SourceError

FEED = "https://blog.example.com/feed/"
DAY = date(2026, 11, 30)


class FakeArchive:
    """Ten posts per page, as WordPress serves them."""

    def __init__(self, pages=108, missing=()):
        self.pages, self.missing, self.asked = pages, set(missing), []

    def __call__(self, url):
        self.asked.append(url)
        page = int(url.rsplit("paged=", 1)[1])
        if page in self.missing:
            raise SourceError(f"cannot fetch feed {url}: HTTP Error 404")
        return [article(f"https://blog.example.com/p{page}-{i}") for i in range(10)]


def source(day=DAY, archive=None):
    return ArchiveSource(
        FEED, "Archive", 108, today=lambda: day, read=archive or FakeArchive()
    )


def test_same_day_same_post_marked_evergreen():
    first, second = source().fetch(), source().fetch()
    assert first == second and len(first) == 1
    assert first[0].evergreen


def test_consecutive_days_use_different_pages():
    urls = {
        source(DAY + timedelta(days=i)).fetch()[0].url.split("-")[0] for i in range(108)
    }
    assert len(urls) == 108  # every page once before any repeats


def test_page_comes_back_with_another_post():
    today = source(DAY).fetch()[0].url
    later = source(DAY + timedelta(days=108)).fetch()[0].url
    assert today.split("-")[0] == later.split("-")[0] and today != later


def test_paged_joins_an_existing_query():
    assert page_url(FEED, 3) == "https://blog.example.com/feed/?paged=3"
    assert page_url("https://a.com/?feed=rss2", 3) == "https://a.com/?feed=rss2&paged=3"


def test_missing_page_is_a_source_error():
    archive = FakeArchive(missing=range(1, 109))
    with pytest.raises(SourceError, match="404"):
        source(archive=archive).fetch()


def test_empty_page_is_a_source_error():
    with pytest.raises(SourceError, match="no valid entry"):
        ArchiveSource(
            FEED, "Archive", 108, today=lambda: DAY, read=lambda url: []
        ).fetch()


def test_pages_must_be_positive():
    with pytest.raises(ValueError):
        ArchiveSource(FEED, "Archive", 0)
