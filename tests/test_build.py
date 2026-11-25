from datetime import UTC, datetime

import pytest
from fakes import FakePublisher, FakeSource, article

from journal.app import BuildError, BuildJournal
from journal.ports import SourceError


class FailingSource:
    def fetch(self):
        raise SourceError("feed down")


def at(hour):
    return datetime(2026, 11, 2, hour, tzinfo=UTC)


def build(*sources):
    publisher = FakePublisher()
    report = BuildJournal(list(sources), publisher).run()
    return publisher, report


def test_gathers_from_every_source():
    a = FakeSource([article("https://a.com/1"), article("https://a.com/2")])
    b = FakeSource([article("https://b.com/1"), article("https://b.com/2")])
    publisher, _ = build(a, b)
    assert {x.url for x in publisher.published} == {
        "https://a.com/1",
        "https://a.com/2",
        "https://b.com/1",
        "https://b.com/2",
    }


def test_failing_source_is_reported_and_others_published():
    publisher, report = build(FailingSource(), FakeSource([article("https://a.com/1")]))
    assert [x.url for x in publisher.published] == ["https://a.com/1"]
    assert [str(e) for e in report.errors] == ["feed down"]


def test_all_sources_failing_does_not_publish():
    publisher = FakePublisher()
    publisher.published = None
    with pytest.raises(BuildError, match="feed down"):
        BuildJournal([FailingSource(), FailingSource()], publisher).run()
    assert publisher.published is None


def test_no_sources_does_not_publish():
    publisher = FakePublisher()
    publisher.published = None
    with pytest.raises(BuildError):
        BuildJournal([], publisher).run()
    assert publisher.published is None


def test_successful_empty_source_publishes_empty_list():
    publisher, report = build(FakeSource([]))
    assert publisher.published == [] and report.articles == []


def test_dedup_keeps_first_occurrence():
    first = FakeSource([article("https://x.com/same", title="From first")])
    second = FakeSource([article("https://x.com/same", title="From second")])
    publisher, _ = build(first, second)
    assert [x.title for x in publisher.published] == ["From first"]


def test_ordered_newest_first():
    source = FakeSource(
        [
            article("https://a.com/9", published_at=at(9)),
            article("https://a.com/11", published_at=at(11)),
            article("https://a.com/10", published_at=at(10)),
        ]
    )
    publisher, _ = build(source)
    assert [x.published_at.hour for x in publisher.published] == [11, 10, 9]


def test_ties_ordered_by_url():
    source = FakeSource(
        [
            article("https://a.com/b", published_at=at(9)),
            article("https://a.com/a", published_at=at(9)),
        ]
    )
    publisher, _ = build(source)
    assert [x.url for x in publisher.published] == [
        "https://a.com/a",
        "https://a.com/b",
    ]
