import json
import re
from datetime import UTC, date, datetime, timedelta

import pytest
from fakes import article, edition

from journal.adapters import static_site
from journal.adapters.static_site import StaticSitePublisher
from journal.adapters.storage import LocalStorage, StoragePort
from journal.domain import Edition
from journal.ports import HistoryPort, PublisherPort, PublishError

DAY = date(2026, 11, 26)


def publisher(out):
    return StaticSitePublisher(LocalStorage(out))


def publish(out, *articles, day=DAY):
    publisher(out).publish(edition(*articles, day=day))
    return out / manifest(out)[-1]["path"]


def manifest(out):
    return json.loads((out / "editions.json").read_text(encoding="utf-8"))


def read_index(folder):
    return json.loads((folder / "articles.json").read_text(encoding="utf-8"))


def pages(out, archive=False):
    """Every page; without the archive, only pages that show articles."""
    return [
        p.read_text(encoding="utf-8")
        for p in out.rglob("*.html")
        if archive or p != out / "edicoes" / "index.html"
    ]


def snapshot(path):
    return {p.relative_to(path): p.read_bytes() for p in path.rglob("*") if p.is_file()}


@pytest.fixture
def out(tmp_path):
    return tmp_path / "dist"


def test_is_a_publisher(out):
    assert isinstance(publisher(out), PublisherPort)
    assert isinstance(publisher(out), HistoryPort)
    assert isinstance(LocalStorage(out), StoragePort)


# articles.json


def test_writes_articles_json_in_order(out):
    items = [article("https://a.com/2"), article("https://a.com/1")]
    folder = publish(out, *items)
    index = read_index(folder)
    assert [x["url"] for x in index] == ["https://a.com/2", "https://a.com/1"]
    assert index[0] == {
        "id": items[0].id,
        "title": "Title",
        "url": "https://a.com/2",
        "summary": "",
        "source": "fake",
        "published_at": "2026-01-01T00:00:00+00:00",
        "image": None,
        "image_caption": None,
        "image_credit": None,
        "section": None,
    }


def test_non_ascii_kept_as_utf8(out):
    folder = publish(out, article(title="Ciência à noite"))
    assert "Ciência à noite".encode() in (folder / "articles.json").read_bytes()


# pages


def test_index_lists_articles_in_order_with_links(out):
    a = article("https://a.com/1", title="Primeiro", summary="Resumo um")
    b = article("https://a.com/2", title="Segundo", summary="Resumo dois")
    folder = publish(out, a, b)
    index = (folder / "index.html").read_text(encoding="utf-8")
    assert index.index("Primeiro") < index.index("Segundo")
    assert f'href="articles/{a.id}.html"' in index
    assert f'href="articles/{b.id}.html"' in index
    assert "Resumo um" in index and "fake" in index
    assert "Edição de 26 nov 2026" in index


def test_empty_site_says_no_articles(out):
    folder = publish(out)
    assert "Nenhum artigo publicado." in (folder / "index.html").read_text()


def test_article_page_content(out):
    a = article("https://a.com/1", title="Título", summary="Resumo", source="Nature")
    folder = publish(out, a)
    page = (folder / "articles" / f"{a.id}.html").read_text(encoding="utf-8")
    for text in ("Título", "Resumo", "Nature", 'href="https://a.com/1"'):
        assert text in page
    assert 'href="../index.html"' in page


def test_dates_shown_in_edition_timezone(out):
    from zoneinfo import ZoneInfo

    a = article(published_at=datetime(2026, 11, 2, 10, tzinfo=UTC))
    tz = ZoneInfo("America/Sao_Paulo")
    publisher(out).publish(Edition(DAY, (a,), tz))
    for page in pages(out):
        assert "2 nov 2026, 07:00" in page
        assert 'datetime="2026-11-02T10:00:00+00:00"' in page


def test_feed_text_is_escaped(out):
    a = article(title="<script>alert(1)</script>", summary='"><img src=x>')
    publish(out, a)
    for page in pages(out):
        assert "<script" not in page and "<img" not in page
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_image_shown_in_list_and_article_page(out):
    a = article(image="https://cdn.example.com/a.jpg")
    folder = publish(out, a)
    assert read_index(folder)[0]["image"] == "https://cdn.example.com/a.jpg"
    for page in pages(out):
        img = re.search(r"<img [^>]*>", page).group(0)
        assert 'src="https://cdn.example.com/a.jpg"' in img
        assert 'alt=""' in img
        assert 'loading="lazy"' in img
        assert 'referrerpolicy="no-referrer"' in img


def test_no_image_element_without_image(out):
    publish(out, article())
    assert not any("<img" in p or "<figcaption" in p for p in pages(out))


def article_page(folder, a):
    return (folder / "articles" / f"{a.id}.html").read_text(encoding="utf-8")


def test_caption_with_credit_on_article_page(out):
    a = article(
        source="Ars Technica",
        image="https://cdn.example.com/a.jpg",
        image_caption="Asteroid Dimorphos",
        image_credit="ESA",
    )
    folder = publish(out, a)
    caption = re.search(r"<figcaption>(.*?)</figcaption>", article_page(folder, a))
    assert "Asteroid Dimorphos" in caption.group(1)
    assert "Imagem: ESA, via Ars Technica" in caption.group(1)
    assert read_index(folder)[0]["image_credit"] == "ESA"
    assert "<figcaption" not in (folder / "index.html").read_text(encoding="utf-8")


def test_caption_without_credit_names_source(out):
    a = article(source="BBC News World", image="https://cdn.example.com/a.jpg")
    folder = publish(out, a)
    caption = re.search(r"<figcaption>(.*?)</figcaption>", article_page(folder, a))
    assert "Imagem: BBC News World" in caption.group(1)
    assert ", via" not in caption.group(1)


def test_caption_and_credit_are_escaped(out):
    a = article(
        image="https://cdn.example.com/a.jpg",
        image_caption="<script>x()</script>",
        image_credit="<b>ESA</b>",
    )
    folder = publish(out, a)
    page = article_page(folder, a)
    assert "<script" not in page and "<b>" not in page
    assert "&lt;b&gt;ESA&lt;/b&gt;" in page


def test_image_url_is_escaped(out):
    a = article(image='https://cdn.example.com/a.jpg?q="><script>x()</script>')
    publish(out, a)
    for page in pages(out):
        assert "<script" not in page
        assert "&quot;&gt;&lt;script&gt;" in page


def test_site_is_self_contained(out):
    publish(out, article())
    assert (out / "style.css").is_file()
    for page in pages(out, archive=True):
        assert 'lang="pt-BR"' in page
        assert re.search(r'href="(\.\./)*style\.css"', page)
        assert "<script" not in page
        internal = [h for h in re.findall(r'href="([^"]+)"', page) if "://" not in h]
        assert internal and not any(h.startswith("/") for h in internal)


# editions


def test_edition_folder_named_by_date(out):
    folder = publish(out, article())
    assert folder == out / "edicoes" / "2026-11-26"
    assert manifest(out) == [
        {
            "date": "2026-11-26",
            "revision": 1,
            "path": "edicoes/2026-11-26/",
            "articles": 1,
            "published_at": manifest(out)[0]["published_at"],
        }
    ]


def test_front_page_shows_latest_edition_with_links_into_it(out):
    publish(out, article("https://a.com/old"), day=date(2026, 11, 25))
    new = article("https://a.com/new", title="Nova", summary="Resumo")
    publish(out, new)
    front = (out / "index.html").read_text(encoding="utf-8")
    assert "Nova" in front and "Edição de 26 nov 2026" in front
    assert f'href="edicoes/2026-11-26/articles/{new.id}.html"' in front
    assert 'href="edicoes/index.html"' in front


def test_same_day_publish_adds_revision_without_overwriting(out):
    first = publish(out, article("https://a.com/1"))
    before = snapshot(first)
    second = publish(out, article("https://a.com/2"))
    assert second == out / "edicoes" / "2026-11-26-2"
    assert snapshot(first) == before
    assert [e["revision"] for e in manifest(out)] == [1, 2]
    assert "(revisão 2)" in (out / "index.html").read_text(encoding="utf-8")


def test_existing_folder_not_in_manifest_is_not_overwritten(out):
    publish(out, article())
    (out / "editions.json").write_text("[]")  # manifest lost
    folder = publish(out, article("https://a.com/x"))
    assert folder == out / "edicoes" / "2026-11-26-2"


def test_archive_lists_editions_newest_first(out):
    publish(out, article(), day=date(2026, 11, 25))
    publish(out, article(), article("https://a.com/2"))
    archive = (out / "edicoes" / "index.html").read_text(encoding="utf-8")
    assert archive.index("26 nov 2026") < archive.index("25 nov 2026")
    assert 'href="2026-11-26/index.html"' in archive
    assert "2 artigos" in archive


def test_article_page_links_back_to_its_edition(out):
    a = article()
    folder = publish(out, a)
    page = (folder / "articles" / f"{a.id}.html").read_text(encoding="utf-8")
    assert 'href="../index.html"' in page
    assert 'href="../../../style.css"' in page


# failure and safety


def test_failed_publish_keeps_front_page_and_manifest(out, monkeypatch):
    publish(out, article("https://a.com/a"))
    front, listed = (out / "index.html").read_bytes(), manifest(out)

    def broken(*_args):
        raise OSError("disk full")

    monkeypatch.setattr(static_site, "_article_page", broken)
    with pytest.raises(PublishError, match="disk full"):
        publish(out, article("https://a.com/b"))
    assert (out / "index.html").read_bytes() == front
    assert manifest(out) == listed


def test_corrupt_manifest_raises_publish_error(out):
    publish(out, article())
    (out / "editions.json").write_text("{not json")
    with pytest.raises(PublishError, match="editions.json"):
        publish(out, article())


def test_refuses_unrelated_directory(tmp_path):
    (tmp_path / "notes.txt").write_text("precious")
    with pytest.raises(PublishError, match="refusing"):
        publisher(tmp_path).publish(edition(article()))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["notes.txt"]


def test_accepts_site_from_before_editions(tmp_path):
    (tmp_path / "articles.json").write_text("[]")
    publisher(tmp_path).publish(edition(article()))
    assert (tmp_path / "editions.json").is_file()


def test_publishes_into_empty_directory(out):
    out.mkdir()
    publish(out, article())
    assert (out / "index.html").is_file()


def test_storage_rejects_keys_outside_root(out):
    with pytest.raises(PublishError, match="outside"):
        LocalStorage(out).write("../escape.txt", b"x")


# history (seen.json)


def test_history_lists_stories_from_earlier_days_only(out):
    a, b = article("https://a.com/a"), article("https://a.com/b")
    publish(out, a, day=date(2026, 11, 25))
    publish(out, b)
    history = publisher(out)
    assert history.published_before(date(2026, 11, 26)) == {a.key}
    assert history.published_before(date(2026, 11, 27)) == {a.key, b.key}
    assert history.published_before(date(2026, 11, 25)) == set()


def test_history_keeps_first_date_on_revision(out):
    a = article()
    publish(out, a, day=date(2026, 11, 25))
    publish(out, a)
    assert publisher(out).published_before(date(2026, 11, 26)) == {a.key}


def test_history_forgets_after_retention(out):
    a = article("https://a.com/a")
    publish(out, a, day=date(2026, 8, 1))
    publish(out, article("https://a.com/b"), day=date(2026, 11, 26))
    assert a.key not in publisher(out).published_before(date(2026, 11, 27))


def test_empty_site_has_no_history(out):
    assert publisher(out).published_before(DAY) == set()


def test_corrupt_history_raises_publish_error(out):
    publish(out, article())
    (out / "seen.json").write_text("[]")
    with pytest.raises(PublishError, match="seen.json"):
        publisher(out).published_before(DAY)


# sections


def test_edition_grouped_by_section_with_headings(out):
    a = article("https://a.com/1", title="Ciencia 1", section="Ciência")
    b = article("https://a.com/2", title="Tech 1", section="Tecnologia")
    c = article("https://a.com/3", title="Solta")
    folder = publish(out, a, b, c)
    index = (folder / "index.html").read_text(encoding="utf-8")
    assert index.index('<h1 id="ciencia">Ciência</h1>') < index.index("Ciencia 1")
    assert index.index("Ciencia 1") < index.index('<h1 id="tecnologia">Tecnologia</h1>')
    assert index.index('<h1 id="tecnologia">Tecnologia</h1>') < index.index(
        '<h1 id="outras">Outras</h1>'
    )
    assert read_index(folder)[0]["section"] == "Ciência"


def test_no_section_headings_without_sections(out):
    folder = publish(out, article())
    assert "<h1>" not in (folder / "index.html").read_text(encoding="utf-8")


# editions menu


def menu(page):
    return re.search(r'<nav class="editions-menu".*?</nav>', page, re.S).group(0)


def test_menu_lists_editions_newest_first_and_marks_current(out):
    publish(out, article("https://a.com/old"), day=date(2026, 11, 25))
    publish(out, article("https://a.com/new"))
    front = menu((out / "index.html").read_text(encoding="utf-8"))
    assert front.index("26/11/2026") < front.index("25/11/2026")
    assert front.count('aria-current="page"') == 1
    assert '<a href="edicoes/2026-11-26/index.html" aria-current="page">' in front
    assert 'href="index.html">Última edição' in front
    assert 'href="edicoes/index.html">Todas as edições' in front
    page = (out / "edicoes" / "2026-11-26" / "index.html").read_text(encoding="utf-8")
    assert 'href="../../edicoes/2026-11-25/index.html">25/11/2026' in menu(page)


def test_menu_shows_revision_number(out):
    publish(out, article("https://a.com/1"))
    publish(out, article("https://a.com/2"))
    front = menu((out / "index.html").read_text(encoding="utf-8"))
    assert 'aria-current="page">26/11/2026 · 2</a>' in front
    assert ">26/11/2026</a>" in front


def test_menu_keeps_the_30_most_recent(out):
    for back in range(30, -1, -1):
        publish(out, article(), day=DAY - timedelta(days=back))
    front = menu((out / "index.html").read_text(encoding="utf-8"))
    assert len(re.findall(r"<li>", front)) == 30
    assert "28/10/2026" in front and "27/10/2026" not in front


def test_every_page_has_the_menu(out):
    a = article()
    folder = publish(out, a)
    assert all('class="editions-menu"' in page for page in pages(out, archive=True))
    page = (folder / "articles" / f"{a.id}.html").read_text(encoding="utf-8")
    assert 'href="../../../edicoes/2026-11-26/index.html" aria-current' in menu(page)


# section index


def test_section_index_links_to_each_section_in_order(out):
    a = article("https://a.com/1", section="Ciência")
    b = article("https://a.com/2", section="Brasil e mundo")
    page = (publish(out, a, b) / "index.html").read_text(encoding="utf-8")
    nav = re.search(r'<nav class="sections".*?</nav>', page).group(0)
    assert nav.index('href="#ciencia"') < nav.index('href="#brasil-e-mundo"')
    assert '<h1 id="brasil-e-mundo">Brasil e mundo</h1>' in page
    assert page.index('class="edition"') < page.index('class="sections"')


def test_no_section_index_without_sections(out):
    page = (publish(out, article()) / "index.html").read_text(encoding="utf-8")
    assert 'class="sections"' not in page


def test_article_without_summary_or_image_links_to_its_source(out):
    bare = article("https://news.example/x", title="Só link")
    folder = publish(out, bare)
    index = (folder / "index.html").read_text(encoding="utf-8")
    assert '<a href="https://news.example/x" rel="noopener noreferrer">Só link' in index
    assert f"articles/{bare.id}.html" not in index
    assert (folder / "articles" / f"{bare.id}.html").is_file()
