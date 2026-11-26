from datetime import UTC, datetime, timedelta

import pytest
from fakes import FakePublisher, FakeSource, article

from journal.app import BuildError, BuildJournal, KeywordFilter
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
    with pytest.raises(BuildError, match="feed down"):
        BuildJournal([FailingSource(), FailingSource()], publisher).run()
    assert publisher.edition is None


def test_no_sources_does_not_publish():
    publisher = FakePublisher()
    with pytest.raises(BuildError):
        BuildJournal([], publisher).run()
    assert publisher.edition is None


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


def test_filter_keeps_matching_articles():
    source = FakeSource(
        [
            article("https://a.com/1", title="Copom mantém a Selic"),
            article("https://a.com/2", title="Time vence clássico"),
        ]
    )
    publisher = FakePublisher()
    report = BuildJournal([source], publisher, KeywordFilter(["selic"])).run()
    assert [x.url for x in publisher.published] == ["https://a.com/1"]
    assert report.fetched == 2


def test_filter_removing_everything_publishes_empty_list():
    publisher = FakePublisher()
    source = FakeSource([article("https://a.com/1", title="Futebol")])
    BuildJournal([source], publisher, KeywordFilter(["selic"])).run()
    assert publisher.edition is not None and publisher.published == []


def test_max_articles_keeps_newest():
    source = FakeSource(
        [
            article("https://a.com/9", published_at=at(9)),
            article("https://a.com/10", published_at=at(10)),
            article("https://a.com/11", published_at=at(11)),
        ]
    )
    publisher = FakePublisher()
    BuildJournal([source], publisher, max_articles=2).run()
    assert [x.url for x in publisher.published] == [
        "https://a.com/11",
        "https://a.com/10",
    ]


NOW = datetime(2026, 11, 10, 12, tzinfo=UTC)


def run_at(sources, **options):
    publisher = FakePublisher()
    report = BuildJournal(sources, publisher, now=lambda: NOW, **options).run()
    return publisher, report


@pytest.mark.parametrize(
    "variant",
    [
        "http://example.com/news/1",
        "https://www.example.com/news/1",
        "https://example.com/news/1/",
        "https://example.com/news/1#comments",
        "https://example.com/news/1?utm_source=rss&utm_medium=feed",
        "https://EXAMPLE.com/news/1?fbclid=abc",
    ],
)
def test_dedup_ignores_url_noise(variant):
    first = FakeSource([article("https://example.com/news/1", title="first")])
    second = FakeSource([article(variant, title="second", published_at=NOW)])
    publisher, report = run_at([first, second])
    assert [a.title for a in publisher.published] == ["first"]
    assert report.fetched == 1


def test_dedup_keeps_meaningful_query():
    a = FakeSource(
        [article("https://example.com/?p=1"), article("https://example.com/?p=2")]
    )
    publisher, _ = run_at([a])
    assert len(publisher.published) == 2


def test_max_age_drops_stale_articles():
    fresh = article("https://a.com/fresh", published_at=NOW - timedelta(days=1))
    stale = article("https://a.com/stale", published_at=NOW - timedelta(days=3))
    publisher, report = run_at([FakeSource([fresh, stale])], max_age_days=2)
    assert [a.url for a in publisher.published] == ["https://a.com/fresh"]
    assert report.fetched == 2


def test_far_future_articles_dropped_without_filter():
    soon = article("https://a.com/soon", published_at=NOW + timedelta(hours=3))
    far = article("https://a.com/far", published_at=NOW + timedelta(days=2))
    publisher, _ = run_at([FakeSource([soon, far])])
    assert [a.url for a in publisher.published] == ["https://a.com/soon"]


class BuggySource:
    name = "Buggy"

    def fetch(self):
        raise TypeError("boom")


def test_unexpected_source_exception_is_isolated():
    publisher, report = run_at(
        [BuggySource(), FakeSource([article("https://a.com/1")])]
    )
    assert [a.url for a in publisher.published] == ["https://a.com/1"]
    assert len(report.errors) == 1
    assert "Buggy" in str(report.errors[0]) and "boom" in str(report.errors[0])


def test_only_buggy_sources_fail_the_build():
    with pytest.raises(BuildError, match="boom"):
        run_at([BuggySource()])


def test_edition_date_uses_configured_timezone():
    from zoneinfo import ZoneInfo

    late = datetime(2026, 11, 27, 2, tzinfo=UTC)  # still the 26th in São Paulo
    publisher = FakePublisher()
    BuildJournal(
        [FakeSource([])],
        publisher,
        now=lambda: late,
        timezone=ZoneInfo("America/Sao_Paulo"),
    ).run()
    assert publisher.edition.date.isoformat() == "2026-11-26"
