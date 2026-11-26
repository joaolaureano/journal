import json
import re
from datetime import UTC, datetime

import pytest
from fakes import article

from journal.adapters import static_site
from journal.adapters.static_site import StaticSitePublisher
from journal.ports import PublisherPort, PublishError


def read_index(out):
    return json.loads((out / "articles.json").read_text(encoding="utf-8"))


def pages(out):
    return [p.read_text(encoding="utf-8") for p in out.rglob("*.html")]


def snapshot(path):
    return {p.relative_to(path): p.read_bytes() for p in path.rglob("*") if p.is_file()}


@pytest.fixture
def out(tmp_path):
    return tmp_path / "dist"


def test_is_a_publisher(out):
    assert isinstance(StaticSitePublisher(out), PublisherPort)


# articles.json


def test_writes_articles_json_in_order(out):
    items = [article("https://a.com/2"), article("https://a.com/1")]
    StaticSitePublisher(out).publish(items)
    index = read_index(out)
    assert [x["url"] for x in index] == ["https://a.com/2", "https://a.com/1"]
    assert index[0] == {
        "id": items[0].id,
        "title": "Title",
        "url": "https://a.com/2",
        "summary": "",
        "source": "fake",
        "published_at": "2026-01-01T00:00:00+00:00",
        "image": None,
    }


def test_non_ascii_kept_as_utf8(out):
    StaticSitePublisher(out).publish([article(title="Ciência à noite")])
    assert "Ciência à noite".encode() in (out / "articles.json").read_bytes()


def test_republish_replaces_index(out):
    publisher = StaticSitePublisher(out)
    publisher.publish([article("https://a.com/old")])
    publisher.publish([article("https://a.com/new")])
    assert [x["url"] for x in read_index(out)] == ["https://a.com/new"]


# pages


def test_index_lists_articles_in_order_with_links(out):
    a = article("https://a.com/1", title="Primeiro", summary="Resumo um")
    b = article("https://a.com/2", title="Segundo")
    StaticSitePublisher(out).publish([a, b])
    index = (out / "index.html").read_text(encoding="utf-8")
    assert index.index("Primeiro") < index.index("Segundo")
    assert f'href="articles/{a.id}.html"' in index
    assert f'href="articles/{b.id}.html"' in index
    assert "Resumo um" in index and "fake" in index


def test_empty_site_says_no_articles(out):
    StaticSitePublisher(out).publish([])
    assert "Nenhum artigo publicado." in (out / "index.html").read_text()


def test_article_page_content(out):
    a = article("https://a.com/1", title="Título", summary="Resumo", source="Nature")
    StaticSitePublisher(out).publish([a])
    page = (out / "articles" / f"{a.id}.html").read_text(encoding="utf-8")
    for text in ("Título", "Resumo", "Nature", 'href="https://a.com/1"'):
        assert text in page
    assert 'href="../index.html"' in page


def test_dates_shown_in_utc_portuguese(out):
    when = datetime(2026, 11, 2, 10, tzinfo=UTC)
    a = article(published_at=when)
    StaticSitePublisher(out).publish([a])
    for page in pages(out):
        assert "2 nov 2026, 10:00 UTC" in page
        assert 'datetime="2026-11-02T10:00:00+00:00"' in page


def test_feed_text_is_escaped(out):
    a = article(title="<script>alert(1)</script>", summary='"><img src=x>')
    StaticSitePublisher(out).publish([a])
    for page in pages(out):
        assert "<script" not in page and "<img" not in page
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_image_shown_in_list_and_article_page(out):
    a = article(image="https://cdn.example.com/a.jpg")
    StaticSitePublisher(out).publish([a])
    assert read_index(out)[0]["image"] == "https://cdn.example.com/a.jpg"
    for page in pages(out):
        img = re.search(r"<img [^>]*>", page).group(0)
        assert 'src="https://cdn.example.com/a.jpg"' in img
        assert 'alt=""' in img
        assert 'loading="lazy"' in img
        assert 'referrerpolicy="no-referrer"' in img


def test_no_image_element_without_image(out):
    StaticSitePublisher(out).publish([article()])
    assert not any("<img" in page for page in pages(out))


def test_image_url_is_escaped(out):
    a = article(image='https://cdn.example.com/a.jpg?q="><script>x()</script>')
    StaticSitePublisher(out).publish([a])
    for page in pages(out):
        assert "<script" not in page
        assert "&quot;&gt;&lt;script&gt;" in page


def test_site_is_self_contained(out):
    StaticSitePublisher(out).publish([article()])
    assert (out / "style.css").is_file()
    for page in pages(out):
        assert 'lang="pt-BR"' in page
        assert re.search(r'href="(\.\./)?style\.css"', page)
        assert "<script" not in page
        internal = [h for h in re.findall(r'href="([^"]+)"', page) if "://" not in h]
        assert internal and not any(h.startswith("/") for h in internal)


# replacement and safety


def test_article_removed_between_publishes(out):
    a, b = article("https://a.com/a"), article("https://a.com/b")
    publisher = StaticSitePublisher(out)
    publisher.publish([a, b])
    publisher.publish([a])
    assert sorted(p.name for p in (out / "articles").iterdir()) == [f"{a.id}.html"]
    assert sorted(p.name for p in out.parent.iterdir()) == ["dist"]


def test_failed_publish_keeps_previous_site(out, monkeypatch):
    publisher = StaticSitePublisher(out)
    publisher.publish([article("https://a.com/a")])
    before = snapshot(out)

    def broken(_article):
        raise OSError("disk full")

    monkeypatch.setattr(static_site, "_article_page", broken)
    with pytest.raises(PublishError, match="disk full"):
        publisher.publish([article("https://a.com/b")])
    assert snapshot(out) == before
    assert sorted(p.name for p in out.parent.iterdir()) == ["dist"]


def test_refuses_unrelated_directory(tmp_path):
    (tmp_path / "notes.txt").write_text("precious")
    with pytest.raises(PublishError, match="refusing"):
        StaticSitePublisher(tmp_path).publish([article()])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["notes.txt"]
    assert (tmp_path / "notes.txt").read_text() == "precious"


def test_publishes_into_empty_directory(out):
    out.mkdir()
    StaticSitePublisher(out).publish([article()])
    assert (out / "index.html").is_file()
