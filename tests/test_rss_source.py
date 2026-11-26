import socket
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from journal.adapters.rss import (
    SUMMARY_LIMIT,
    RssSource,
    _rfc822_pt,
    body_html,
    plain_text,
    summary_text,
)
from journal.ports import SourceError, SourcePort

FIXTURES = Path(__file__).parent / "fixtures"


def source(name="feed.xml", **kwargs):
    return RssSource((FIXTURES / name).as_uri(), "Fixture", **kwargs)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Records the retry delays instead of waiting."""
    waited = []
    monkeypatch.setattr("journal.adapters.rss.time.sleep", waited.append)
    return waited


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
        "Captioned": "https://cdn.example.com/d.jpg",
        "Credit without image": None,
    }


def test_image_caption_and_credit_come_from_feed_media():
    found = {
        a.title: (a.image_caption, a.image_credit) for a in source("images.xml").fetch()
    }
    assert found["Captioned"] == ("Asteroid Dimorphos", "ESA")
    assert found["Thumbnail"] == (None, None)
    assert found["Credit without image"] == (None, None)


def test_truncated_response_raises_source_error():
    with socket.create_server(("127.0.0.1", 0)) as server:
        port = server.getsockname()[1]

        def cut_transfer():
            conn, _ = server.accept()
            with conn:
                conn.recv(4096)
                conn.sendall(
                    b"HTTP/1.1 200 OK\r\nContent-Length: 100000\r\n\r\n<rss version="
                )

        thread = threading.Thread(target=cut_transfer)
        thread.start()
        try:
            with pytest.raises(SourceError, match="127.0.0.1"):
                RssSource(
                    f"http://127.0.0.1:{port}/feed", "Cut", timeout=5, retries=0
                ).fetch()
        finally:
            thread.join()


def test_atom_feed_is_read():
    [entry] = source("atom.xml").fetch()
    assert entry.title == "Atom entry"
    assert entry.url == "https://atom.example.com/post"
    assert entry.summary == "Atom summary"
    assert entry.published_at == datetime(2026, 11, 2, 10, tzinfo=UTC)


def test_wordpress_footer_removed_and_image_from_full_text():
    by_title = {a.title: a for a in source("wordpress.xml").fetch()}
    samu = by_title["Nova base do Samu"]
    assert samu.summary == "Prédio com 229 metros quadrados"
    assert samu.image == "https://wp.example.com/samu.webp"
    assert by_title["English footer"].summary == "Short teaser"
    assert by_title["English footer"].image is None


def test_long_summary_is_cut_at_a_word():
    text = summary_text("<p>" + "palavra " * 100 + "</p>")
    assert len(text) <= SUMMARY_LIMIT + 1
    assert text.endswith("palavra…")
    assert summary_text("curto") == "curto"


def serve(statuses):
    """HTTP server answering each request with the next status; 200 serves feed.xml."""
    feed = (FIXTURES / "feed.xml").read_bytes()
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status = statuses[min(len(requests), len(statuses) - 1)]
            requests.append(status)
            self.send_response(status)
            self.end_headers()
            if status == 200:
                self.wfile.write(feed)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/feed", requests


def test_server_error_then_success_is_retried(sleeps):
    server, url, requests = serve([503, 200])
    with server:
        articles = RssSource(url, "Flaky").fetch()
        server.shutdown()
    assert articles and requests == [503, 200]
    assert sleeps == [1]


def test_not_found_is_not_retried(sleeps):
    server, url, requests = serve([404])
    with server:
        with pytest.raises(SourceError, match="404"):
            RssSource(url, "Gone").fetch()
        server.shutdown()
    assert requests == [404] and sleeps == []


def test_persistent_failure_gives_up_after_the_retries(sleeps):
    server, url, requests = serve([500])
    with server:
        with pytest.raises(SourceError, match="500"):
            RssSource(url, "Down").fetch()
        server.shutdown()
    assert requests == [500, 500, 500]
    assert sleeps == [1, 2]


@pytest.mark.parametrize(
    "html", ['<a href="https://n.example/1">Comments</a>', "comments"]
)
def test_comments_only_summary_is_empty(html):
    assert summary_text(html) == ""


# full text (body)


def full(**kwargs):
    return {a.title: a for a in source("fulltext.xml", **kwargs).fetch()}


def test_body_is_off_by_default():
    assert all(a.body is None for a in full().values())


def test_body_from_content_encoded_keeps_paragraphs_and_photos():
    a = full(full_text=True)["In content"]
    assert a.summary == "Teaser curto."
    assert a.body.count("<p>") == 3
    assert "Segundo parágrafo" in a.body
    assert (
        '<figure><img src="https://site.example.com/f/b.jpg" alt="Ponte"'
        ' loading="lazy" referrerpolicy="no-referrer"><figcaption>A ponte'
        "</figcaption></figure>"
    ) in a.body


def test_body_drops_cover_and_wordpress_footer():
    a = full(full_text=True)["In content"]
    assert a.image == "https://cdn.example.com/a.jpg"
    assert "a.jpg" not in a.body
    assert "apareceu primeiro" not in a.body


def test_body_from_long_summary():
    a = full(full_text=True)["In summary"]
    assert a.summary.endswith("…") and len(a.summary) <= SUMMARY_LIMIT + 1
    assert a.body.startswith("<p>palavra") and a.body.endswith("<p>Fim.</p>")


def test_no_body_when_nothing_beyond_the_summary():
    assert full(full_text=True)["Short"].body is None


BASE = "https://site.com/n/1"


@pytest.mark.parametrize(
    ("html", "body"),
    [
        (
            '<p onclick="x()">Oi <script>alert(1)</script>'
            '<iframe src="https://e.com"></iframe></p>',
            "<p>Oi </p>",
        ),
        ('<div class="x"><span style="color:red">texto</span></div>', "texto"),
        ("<h1>A</h1><h5>B</h5>", "<h2>A</h2><h4>B</h4>"),
        (
            '<img src="/f/a.jpg">',
            '<img src="https://site.com/f/a.jpg" alt="" loading="lazy"'
            ' referrerpolicy="no-referrer">',
        ),
        (
            '<a href="javascript:alert(1)">clique</a>',
            '<a rel="noopener noreferrer">clique</a>',
        ),
        (
            '<a href="/x">ir</a>',
            '<a href="https://site.com/x" rel="noopener noreferrer">ir</a>',
        ),
        ('<img src="https://t.com/p.gif" width="1" height="1">', ""),
        ('<img src="data:image/png;base64,AAAA">', ""),
        (
            '<img src="data:image/gif;base64,R0" data-src="https://c.com/real.jpg">',
            '<img src="https://c.com/real.jpg" alt="" loading="lazy"'
            ' referrerpolicy="no-referrer">',
        ),
        ("<blockquote><p>sem fim", "<blockquote><p>sem fim</p></blockquote>"),
        ("<p>a</em></blockquote>b</p>", "<p>ab</p>"),
        ("<svg><svg></svg><p>x</p></svg><p>y</p>", "<p>y</p>"),
        (
            "&lt;script&gt;alert(1)&lt;/script&gt;",
            "&lt;script&gt;alert(1)&lt;/script&gt;",
        ),
        (
            '<img src="https://c.com/a.jpg" /><br />  Primeira linha\nSegunda linha',
            '<p><img src="https://c.com/a.jpg" alt="" loading="lazy"'
            ' referrerpolicy="no-referrer"></p><p>Primeira linha</p>'
            "<p>Segunda linha</p>",
        ),
    ],
    ids=[
        "script-handlers-frames",
        "unknown-unwrapped",
        "headings-shift",
        "relative-image",
        "javascript-link",
        "relative-link",
        "tracking-pixel",
        "data-image",
        "lazy-image",
        "unclosed-tags-closed",
        "stray-end-tags",
        "nested-dropped",
        "escaped-text-stays-text",
        "plain-text-lines",
    ],
)
def test_body_html_allowlist(html, body):
    assert body_html(html, BASE) == body


def test_body_html_attribute_values_cannot_break_out():
    body = body_html(
        '<img src="https://c.com/a.jpg" alt="x&quot; onerror=&quot;y">', BASE
    )
    assert body == (
        '<img src="https://c.com/a.jpg" alt="x&quot; onerror=&quot;y"'
        ' loading="lazy" referrerpolicy="no-referrer">'
    )


@pytest.mark.parametrize(
    ("html", "summary"),
    [
        (
            '<p>Article URL: <a href="https://a.com">https://a.com</a></p>'
            '<p>Comments URL: <a href="https://news.ycombinator.com/item?id=1">'
            "https://news.ycombinator.com/item?id=1</a></p>"
            "<p>Points: 294</p><p># Comments: 160</p>",
            "",
        ),
        (
            "<p>Como vocês testam isso?</p><hr><p>Comments URL: "
            '<a href="https://news.ycombinator.com/item?id=2">'
            "https://news.ycombinator.com/item?id=2</a></p>"
            "<p>Points: 12</p><p># Comments: 3</p>",
            "Como vocês testam isso?",
        ),
    ],
    ids=["link", "text"],
)
def test_hnrss_statistics_are_not_a_summary(html, summary):
    assert summary_text(html) == summary


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Qui, 26 Nov 2026 10:08:44 -0300",
            datetime(2026, 11, 26, 13, 8, 44, tzinfo=UTC),
        ),
        ("Sáb, 05 Dez 2026 08:00:00 -0300", datetime(2026, 12, 5, 11, tzinfo=UTC)),
        ("Ter, 03 Fev 2026 23:30:00 GMT", datetime(2026, 2, 3, 23, 30, tzinfo=UTC)),
        ("ontem à tarde", None),
        (None, None),
    ],
    ids=["uol", "portuguese-month", "gmt", "not-a-date", "missing"],
)
def test_portuguese_rfc822_dates(text, expected):
    assert _rfc822_pt(text) == expected


def test_feed_with_portuguese_dates_is_read(tmp_path):
    feed = tmp_path / "uol.xml"
    feed.write_text(
        "<rss><channel><title>UOL</title><item><title>Notícia</title>"
        "<link>https://a.com/1</link><description>Resumo</description>"
        "<pubDate>Qui, 26 Nov 2026 10:08:44 -0300</pubDate></item>"
        "<item><title>Sem data</title><link>https://a.com/2</link>"
        "<pubDate>ontem à tarde</pubDate></item></channel></rss>",
        encoding="utf-8",
    )
    [a] = RssSource(feed.as_uri(), "UOL").fetch()
    assert a.published_at == datetime(2026, 11, 26, 13, 8, 44, tzinfo=UTC)
