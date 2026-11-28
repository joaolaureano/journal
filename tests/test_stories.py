from datetime import UTC, datetime, timedelta

from fakes import FakeGrouper, FakePublisher, FakeSource, article

from journal.app import BuildJournal, Sectioned

NOW = datetime(2026, 11, 30, 11, 0, tzinfo=UTC)


class Named(FakeSource):
    def __init__(self, name, articles):
        super().__init__(articles)
        self.name = name


def item(slug, source, hours_ago=1.0):
    return article(
        f"https://{source}.com/{slug}",
        source=source,
        title=slug,
        published_at=NOW - timedelta(hours=hours_ago),
    )


def build(sources, grouper, **options):
    publisher = FakePublisher()
    report = BuildJournal(
        sources, publisher, now=lambda: NOW, grouper=grouper, **options
    ).run()
    return publisher.edition, report


def urls(story):
    return sorted(a.url for a in story.items)


def test_same_fact_from_three_outlets_is_one_story():
    g1, cnn, jota, alone = (
        item("stf", "g1"),
        item("stf", "cnn"),
        item("stf", "jota"),
        item("other", "g1"),
    )
    sources = [Named("g1", [g1, alone]), Named("cnn", [cnn]), Named("jota", [jota])]
    edition, _ = build(sources, FakeGrouper([g1.url, cnn.url, jota.url]))
    first, second = edition.stories
    assert urls(first) == sorted([g1.url, cnn.url, jota.url])
    assert first.sources == ("g1", "cnn", "jota")  # lead from the first source
    assert urls(second) == [alone.url]


def test_item_keeps_its_first_group_only():
    x, y, z = item("x", "a"), item("y", "b"), item("z", "c")
    edition, _ = build(
        [FakeSource([x, y, z])], FakeGrouper([x.url, y.url], [y.url, z.url])
    )
    assert [urls(s) for s in edition.stories] == [sorted([x.url, y.url]), [z.url]]


def test_section_by_majority_then_configured_order():
    p1, p2, e1 = item("p1", "a"), item("p2", "b"), item("e1", "c")
    sources = [
        Sectioned(FakeSource([p1, p2]), "Política"),
        Sectioned(FakeSource([e1]), "Economia"),
    ]
    edition, _ = build(sources, FakeGrouper([p1.url, p2.url, e1.url]))
    assert edition.stories[0].section == "Política"
    edition, _ = build(sources, FakeGrouper([p1.url, e1.url]))
    assert edition.stories[0].section == "Política"  # 1 to 1: configured first wins


def test_lead_is_the_newest_item_of_the_first_source():
    older, newer = item("old", "g1", hours_ago=5), item("new", "g1", hours_ago=1)
    cnn = item("x", "cnn", hours_ago=0.5)
    sources = [Named("g1", [older, newer]), Named("cnn", [cnn])]
    edition, _ = build(sources, FakeGrouper([cnn.url, older.url, newer.url]))
    assert edition.stories[0].lead == newer


def test_ten_stories_with_every_section_ranked_by_coverage():
    sections = ["Política", "Economia", "Mundo", "Rio Grande do Sul"]
    sources, groups = [], []
    for i, name in enumerate(sections):
        items = [item(f"{name}-{n}", f"s{i}{n}", hours_ago=n + i) for n in range(10)]
        sources.append(Sectioned(FakeSource(items), name))
        if name == "Política":  # three stories covered by several outlets
            groups += [
                [items[0].url, items[1].url, items[2].url],
                [items[3].url, items[4].url],
            ]
    edition, _ = build(sources, FakeGrouper(*groups), max_stories=10)
    stories = edition.stories
    assert len(stories) == 10
    assert {s.section for s in stories} == set(sections)
    coverage = [len(s.sources) for s in stories]
    assert coverage == sorted(coverage, reverse=True) and coverage[:2] == [3, 2]


def test_stories_see_items_cut_from_the_news_list():
    a, b, c = item("a", "x"), item("b", "y"), item("c", "z")
    edition, _ = build(
        [Sectioned(FakeSource([a, b, c]), "Política")],
        FakeGrouper([a.url, b.url, c.url]),
        max_per_section=1,
    )
    assert len(edition.articles) == 1 and len(edition.stories[0].items) == 3


def test_only_news_become_stories():
    news, essay = (
        item("n", "a"),
        article("https://b.com/e", kind="artigo", published_at=NOW),
    )
    grouper = FakeGrouper()
    edition, _ = build([FakeSource([news, essay])], grouper)
    assert grouper.asked == [news]
    assert [urls(s) for s in edition.stories] == [[news.url]]


def test_grouper_failure_keeps_the_edition():
    a = item("a", "x")
    edition, report = build([FakeSource([a])], FakeGrouper(error=RuntimeError("down")))
    assert edition.stories == () and [x.url for x in edition.articles] == [a.url]
    assert report.story_errors == ["down"]


def test_no_grouper_no_stories():
    edition, report = build([FakeSource([item("a", "x")])], None)
    assert edition.stories == () and report.story_errors == []
