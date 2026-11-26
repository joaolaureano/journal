import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest

from journal.adapters.rss import RssSource, plain_text
from journal.ports import SourceError, SourcePort

FIXTURES = Path(__file__).parent / "fixtures"


def source(name="feed.xml", **kwargs):
    return RssSource((FIXTURES / name).as_uri(), "Fixture", **kwargs)


@pytest.fixture
def articles():
    return {a.title: a for a in source().fetch()}


def test_is_a_source():
    assert isinstance(source(), SourcePort)


def test_valid_entries_in_feed_order_with_source_name():
    result = source().fetch()
    assert [a.title for a in result] == [
        "First article",
        "No summary",
        "Only updated date",
        "Offset date",
    ]
    first = result[0]
    assert first.url == "https://example.com/first"
    assert first.published_at == datetime(2026, 11, 2, 10, tzinfo=UTC)
    assert {a.source for a in result} == {"Fixture"}


def test_updated_date_used_when_published_missing(articles):
    assert articles["Only updated date"].published_at == datetime(
        2026, 11, 1, 12, tzinfo=UTC
    )


def test_dates_are_utc(articles):
    when = articles["Offset date"].published_at
    assert when == datetime(2026, 11, 1, 12, tzinfo=UTC)
    assert when.utcoffset().total_seconds() == 0


def test_html_summary_becomes_plain_text(articles):
    assert articles["First article"].summary == "Hello world"


def test_plain_text_drops_script_and_collapses_whitespace():
    html = "<p>Hello&nbsp;<b>world</b></p>\n<script>x()</script>"
    assert plain_text(html) == "Hello world"


def test_missing_summary_is_empty(articles):
    assert articles["No summary"].summary == ""


def test_entry_without_link_is_skipped(articles):
    assert "Missing link" not in articles


def test_unreachable_feed_raises_source_error():
    with pytest.raises(SourceError, match="missing.xml"):
        source("missing.xml").fetch()


def test_slow_feed_raises_source_error():
    # accepts connections (kernel backlog) but never answers
    with socket.create_server(("127.0.0.1", 0)) as server:
        port = server.getsockname()[1]
        slow = RssSource(f"http://127.0.0.1:{port}/feed", "Slow", timeout=0.2)
        with pytest.raises(SourceError):
            slow.fetch()


def test_non_feed_content_raises_source_error():
    with pytest.raises(SourceError, match="not-a-feed.html"):
        source("not-a-feed.html").fetch()


def test_image_comes_from_feed_media():
    images = {a.title: a.image for a in source("images.xml").fetch()}
    assert images == {
        "Thumbnail": "https://cdn.example.com/t.jpg",
        "Enclosure": "https://cdn.example.com/e.jpg",
        "Audio": None,
        "Summary image": None,
        "Bad media": None,
        "Content first": "https://cdn.example.com/c.jpg",
    }
