import json
from collections.abc import Sequence
from datetime import UTC, date, datetime
from html import escape
from importlib.resources import files
from string import Template

from journal.adapters.storage import StoragePort
from journal.domain import Article, Edition
from journal.ports import PublishError

TEMPLATES = files("journal.adapters") / "templates"
MONTHS = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)
MANIFEST = "editions.json"
EDITIONS = "edicoes"


class StaticSitePublisher:
    """Adds one edition per publish under `edicoes/<date>[-<revision>]/`.

    Earlier editions are never rewritten. The edition's files are written first and
    the manifest and front page last, so a failed publish leaves the published site
    pointing at the previous edition.
    """

    def __init__(self, storage: StoragePort):
        self.storage = storage

    def publish(self, edition: Edition) -> None:
        try:
            manifest = self._manifest()
            revision, slug = self._next_slug(manifest, edition.date)
            entry = {
                "date": edition.date.isoformat(),
                "revision": revision,
                "path": f"{EDITIONS}/{slug}/",
                "articles": len(edition.articles),
                "published_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            manifest.append(entry)
            base = entry["path"]
            for a in edition.articles:
                self._put(f"{base}articles/{a.id}.html", _article_page(a, "../../../"))
            self._put(f"{base}articles.json", _index_json(edition.articles))
            self._put(f"{base}index.html", _edition_page(edition, entry, "../../", ""))
            self._put("style.css", _read("style.css"))
            self._put(f"{EDITIONS}/index.html", _archive_page(manifest))
            self._put(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2))
            self._put("index.html", _edition_page(edition, entry, "", base))
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise PublishError(f"cannot publish edition {edition.date}: {exc}") from exc

    def _manifest(self) -> list[dict]:
        raw = self.storage.read(MANIFEST)
        if raw is None:
            return []
        try:
            manifest = json.loads(raw)
        except ValueError as exc:
            raise PublishError(f"{MANIFEST} is not valid JSON: {exc}") from exc
        if not isinstance(manifest, list):
            raise PublishError(f"{MANIFEST} must be a JSON array")
        return manifest

    def _next_slug(self, manifest: list[dict], day: date) -> tuple[int, str]:
        """First revision of `day` not yet in the manifest nor in storage."""
        revision = 1 + sum(e.get("date") == day.isoformat() for e in manifest)
        while True:
            slug = day.isoformat() + ("" if revision == 1 else f"-{revision}")
            if not self.storage.exists(f"{EDITIONS}/{slug}/index.html"):
                return revision, slug
            revision += 1

    def _put(self, key: str, text: str) -> None:
        self.storage.write(key, text.encode("utf-8"))


def _read(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _page(title: str, content: str, root: str) -> str:
    return Template(_read("base.html")).substitute(
        title=escape(title), content=content, root=root
    )


def _day(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def _when(article: Article) -> dict[str, str]:
    d = article.published_at.astimezone(UTC)
    return {"iso": d.isoformat(), "date": f"{_day(d)}, {d:%H:%M} UTC"}


def _edition_label(entry: dict) -> str:
    label = f"Edição de {_day(date.fromisoformat(entry['date']))}"
    return label + (f" (revisão {entry['revision']})" if entry["revision"] > 1 else "")


def _img(article: Article, css_class: str) -> str:
    if not article.image:
        return ""
    return (
        f'<img class="{css_class}" src="{escape(article.image)}" alt="" '
        'loading="lazy" referrerpolicy="no-referrer">'
    )


def _figure(article: Article) -> str:
    if not article.image:
        return ""
    source = escape(article.source)
    credit = (
        f"Imagem: {escape(article.image_credit)}, via {source}"
        if article.image_credit
        else f"Imagem: {source}"
    )
    caption = (
        f"{escape(article.image_caption)} " if article.image_caption else ""
    ) + f'<span class="credit">{credit}</span>'
    return (
        f"<figure>{_img(article, 'photo')}<figcaption>{caption}</figcaption></figure>"
    )


def _edition_page(edition: Edition, entry: dict, root: str, base: str) -> str:
    """Article list of an edition; `base` is the edition folder seen from the page."""
    items = []
    for a in edition.articles:
        w = _when(a)
        summary = f'<p class="summary">{escape(a.summary)}</p>' if a.summary else ""
        items.append(
            f"<li>{_img(a, 'thumb')}"
            f'<h2><a href="{base}articles/{a.id}.html">{escape(a.title)}</a></h2>'
            f'<p class="meta">{escape(a.source)} · '
            f'<time datetime="{w["iso"]}">{w["date"]}</time></p>{summary}</li>'
        )
    listing = (
        '<ol class="articles">\n' + "\n".join(items) + "\n</ol>"
        if items
        else "<p>Nenhum artigo publicado.</p>"
    )
    label = _edition_label(entry)
    content = Template(_read("index.html")).substitute(
        heading=escape(label), items=listing, archive=f"{root}{EDITIONS}/index.html"
    )
    return _page(f"{label} · Journal", content, root=root)


def _count(n: int) -> str:
    return f"{n} artigo" if n == 1 else f"{n} artigos"


def _archive_page(manifest: list[dict]) -> str:
    items = [
        f'<li><a href="{escape(e["path"].removeprefix(EDITIONS + "/"))}index.html">'
        f"{escape(_edition_label(e))}</a>"
        f' <span class="meta">· {_count(int(e["articles"]))}</span></li>'
        for e in reversed(manifest)
    ]
    content = (
        "<h1>Edições</h1>\n" + '<ul class="editions">\n' + "\n".join(items) + "\n</ul>"
    )
    return _page("Edições · Journal", content, root="../")


def _article_page(a: Article, root: str) -> str:
    content = Template(_read("article.html")).substitute(
        title=escape(a.title),
        source=escape(a.source),
        summary=escape(a.summary),
        url=escape(a.url),
        image=_figure(a),
        **_when(a),
    )
    return _page(f"{a.title} · Journal", content, root=root)


def _index_json(articles: Sequence[Article]) -> str:
    index = [
        {
            "id": a.id,
            "title": a.title,
            "url": a.url,
            "summary": a.summary,
            "source": a.source,
            "published_at": a.published_at.isoformat(),
            "image": a.image,
            "image_caption": a.image_caption,
            "image_credit": a.image_credit,
        }
        for a in articles
    ]
    return json.dumps(index, ensure_ascii=False, indent=2)
