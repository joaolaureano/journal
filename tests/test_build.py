import threading
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


class FakeHistory:
    def __init__(self, keys):
        self.keys = set(keys)
        self.asked = None

    def published_before(self, day):
        self.asked = day
        return self.keys


def test_articles_from_earlier_editions_are_dropped():
    old = article("https://a.com/old", published_at=NOW)
    new = article("https://a.com/new", published_at=NOW)
    history = FakeHistory({old.key})
    publisher, report = run_at([FakeSource([old, new])], history=history)
    assert [a.url for a in publisher.published] == ["https://a.com/new"]
    assert report.already_published == 1 and report.fetched == 2
    assert history.asked == NOW.date()


def test_history_matches_url_variants():
    history = FakeHistory({article("https://a.com/x").key})
    variant = article("http://www.a.com/x/?utm_source=rss", published_at=NOW)
    publisher, _ = run_at([FakeSource([variant])], history=history)
    assert publisher.published == []


def test_editions_grouped_by_configured_section_order():
    from journal.app import Sectioned

    tech = Sectioned(
        FakeSource([article("https://t.com/1", published_at=NOW)]), "Tecnologia"
    )
    sci = Sectioned(
        FakeSource([article("https://s.com/1", published_at=NOW - timedelta(hours=1))]),
        "Ciência",
    )
    loose = FakeSource([article("https://l.com/1", published_at=NOW)])
    publisher, _ = run_at([tech, loose, sci])
    assert [a.section for a in publisher.published] == ["Tecnologia", "Ciência", None]


def test_max_per_section_keeps_newest_of_each():
    from journal.app import Sectioned

    busy = Sectioned(
        FakeSource(
            [article(f"https://b.com/{h}", published_at=at(h)) for h in (9, 10, 11)]
        ),
        "Busy",
    )
    calm = Sectioned(
        FakeSource([article("https://c.com/1", published_at=at(8))]), "Calm"
    )
    publisher = FakePublisher()
    BuildJournal([busy, calm], publisher, max_per_section=2).run()
    assert [a.url for a in publisher.published] == [
        "https://b.com/11",
        "https://b.com/10",
        "https://c.com/1",
    ]


def test_edition_carries_timezone():
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Sao_Paulo")
    publisher = FakePublisher()
    BuildJournal([FakeSource([])], publisher, timezone=tz).run()
    assert publisher.edition.timezone is tz


def test_news_do_not_push_articles_out_of_a_section():
    from journal.app import Sectioned

    news = [article(f"https://n.com/{h}", published_at=at(h)) for h in (9, 10, 11)]
    essay = article("https://e.com/1", published_at=at(8), kind="artigo")
    sci = Sectioned(FakeSource([*news, essay]), "Ciência")
    publisher = FakePublisher()
    BuildJournal([sci], publisher, max_per_section=2).run()
    assert [a.url for a in publisher.published] == [
        "https://n.com/11",
        "https://n.com/10",
        "https://e.com/1",
    ]


# AI warm-up


class Summarizer:
    def __init__(self, answers):
        self.answers = answers  # url -> text, None, "slow" or an exception to raise
        self.asked = []

    def warmup(self, a):
        self.asked.append(a.url)
        answer = self.answers.get(a.url, "Resumo.")
        if isinstance(answer, Exception):
            raise answer
        if answer == "slow":
            threading.Event().wait(1)
            return "late"
        return answer


def warm(summarizer, *items, timeout=5):
    publisher = FakePublisher()
    report = BuildJournal(
        [FakeSource(list(items))],
        publisher,
        summarizer=summarizer,
        warmup_timeout=timeout,
    ).run()
    return {a.url: a.warmup for a in publisher.published}, report


def test_only_articles_get_a_warmup():
    s = Summarizer({})
    news, art = article("https://a.com/n"), article("https://a.com/a", kind="artigo")
    warmups, report = warm(s, news, art)
    assert warmups == {"https://a.com/n": None, "https://a.com/a": "Resumo."}
    assert s.asked == ["https://a.com/a"] and report.warmups == 1


def test_warmup_failure_only_skips_that_article():
    s = Summarizer(
        {"https://a.com/1": RuntimeError("API down"), "https://a.com/3": None}
    )
    items = [article(f"https://a.com/{i}", kind="artigo") for i in (1, 2, 3)]
    warmups, report = warm(s, *items)
    assert warmups == {
        "https://a.com/1": None,
        "https://a.com/2": "Resumo.",
        "https://a.com/3": None,
    }
    assert report.warmup_errors == ["API down"]


def test_slow_warmup_is_dropped_after_the_timeout():
    s = Summarizer({"https://a.com/1": "slow"})
    warmups, report = warm(s, article("https://a.com/1", kind="artigo"), timeout=0.05)
    assert warmups == {"https://a.com/1": None}
    assert report.warmup_errors == ["warm-up timed out: 1 articles without it"]


def test_no_summarizer_no_warmups():
    publisher, report = build(FakeSource([article(kind="artigo")]))
    assert publisher.published[0].warmup is None and report.warmup_errors == []


def test_paths_keep_only_matching_links():
    from journal.app import Sectioned

    feed = FakeSource(
        [
            article("https://www.cnnbrasil.com.br/politica/a"),
            article("https://www.cnnbrasil.com.br/esportes/b"),
            article("https://www.cnnbrasil.com.br/politicas/c"),
        ]
    )
    got = Sectioned(feed, "Política", paths=["/politica/"]).fetch()
    assert [(a.url, a.section) for a in got] == [
        ("https://www.cnnbrasil.com.br/politica/a", "Política")
    ]
