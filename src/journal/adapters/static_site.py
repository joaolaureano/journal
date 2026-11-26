import hashlib
import json
import re
import unicodedata
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta, tzinfo
from html import escape
from importlib.resources import files
from itertools import groupby
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
SEEN = "seen.json"  # article key -> date of the first edition that published it
SEEN_RETENTION = timedelta(days=90)
EDITIONS = "edicoes"
MENU_EDITIONS = 30  # the archive lists the rest
LIST_PAGES = {"noticia": "index.html", "artigo": "artigos.html"}  # one page per kind
TABS = {"noticia": "Notícias", "artigo": "Artigos"}
EMPTY = {
    "noticia": "Nenhuma notícia publicada.",
    "artigo": "Nenhum artigo nesta edição.",
}
WORDS_PER_MINUTE = 200


class StaticSitePublisher:
    """Adds one edition per publish under `edicoes/<date>[-<revision>]/`.

    Also the journal's history: `seen.json` remembers which stories each day
    published, so later days do not repeat them (kept for SEEN_RETENTION).

    Earlier editions are never rewritten. The edition's files are written first and
    the manifest and front page last, so a failed publish leaves the published site
    pointing at the previous edition.
    """

    def __init__(self, storage: StoragePort):
        self.storage = storage

    def published_before(self, day: date) -> set[str]:
        return {k for k, first in self._seen().items() if first < day.isoformat()}

    def publish(self, edition: Edition) -> None:
        try:
            manifest = self._manifest()
            seen = self._seen()
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
                page = _article_page(a, edition.timezone, "../../../", manifest, entry)
                self._put(f"{base}articles/{a.id}.html", page)
            self._put(f"{base}articles.json", _index_json(edition.articles))
            for kind, name in LIST_PAGES.items():
                page = _edition_page(edition, entry, manifest, "../../", "", kind)
                self._put(f"{base}{name}", page)
            self._put(_stylesheet(), _read("style.css"))
            self._put("style.css", _read("style.css"))  # for pages from before
            self._put(f"{EDITIONS}/index.html", _archive_page(manifest))
            self._put(SEEN, _seen_json(seen, edition))
            self._put(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2))
            # the root index.html goes last: until then the site shows the previous one
            for kind, name in reversed(LIST_PAGES.items()):
                self._put(name, _edition_page(edition, entry, manifest, "", base, kind))
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

    def _seen(self) -> dict[str, str]:
        raw = self.storage.read(SEEN)
        if raw is None:
            return {}
        try:
            seen = json.loads(raw)
        except ValueError as exc:
            raise PublishError(f"{SEEN} is not valid JSON: {exc}") from exc
        if not isinstance(seen, dict):
            raise PublishError(f"{SEEN} must be a JSON object")
        return seen

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


def _seen_json(seen: dict[str, str], edition: Edition) -> str:
    """Adds the edition's stories (keeping the first date) and drops expired ones."""
    for a in edition.articles:
        seen.setdefault(a.key, edition.date.isoformat())
    oldest = (edition.date - SEEN_RETENTION).isoformat()
    kept = {k: d for k, d in sorted(seen.items()) if d >= oldest}
    return json.dumps(kept, ensure_ascii=False, indent=0)


def _read(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _page(title: str, content: str, root: str, menu: str) -> str:
    return Template(_read("base.html")).substitute(
        title=escape(title),
        content=content,
        root=root,
        menu=menu,
        stylesheet=_stylesheet(),
    )


def _stylesheet() -> str:
    """'style.<hash>.css': a changed stylesheet is a new file, so no cache keeps an old
    one (CloudFront's cache key ignores query strings)."""
    digest = hashlib.sha256(_read("style.css").encode("utf-8")).hexdigest()[:10]
    return f"style.{digest}.css"


def _menu(manifest: list[dict], root: str, current: dict | None) -> str:
    """Latest editions, newest first; `current` is the page's own edition."""
    items = []
    for e in reversed(manifest[-MENU_EDITIONS:]):
        label = f"{date.fromisoformat(e['date']):%d/%m/%Y}"
        label += f" · {e['revision']}" if e["revision"] > 1 else ""
        mark = (
            ' aria-current="page"' if current and e["path"] == current["path"] else ""
        )
        href = escape(f"{root}{e['path']}index.html")
        items.append(f'<li><a href="{href}"{mark}>{label}</a></li>')
    return Template(_read("menu.html")).substitute(
        root=root, archive=f"{root}{EDITIONS}/index.html", items="\n".join(items)
    )


def _day(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def _when(article: Article, tz: tzinfo) -> dict[str, str]:
    """Shown in the edition's timezone; machine-readable timestamp in UTC."""
    d = article.published_at.astimezone(tz)
    iso = article.published_at.astimezone(UTC).isoformat()
    return {"iso": iso, "date": f"{_day(d)}, {d:%H:%M}"}


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


def _edition_page(
    edition: Edition,
    entry: dict,
    manifest: list[dict],
    root: str,
    base: str,
    kind: str = "noticia",
) -> str:
    """List page of one kind; `base` is the edition folder seen from the page."""
    articles = [a for a in edition.articles if a.kind == kind]
    sectioned = any(a.section for a in articles)
    blocks, links = [], []
    for section, group in groupby(articles, key=lambda a: a.section):
        items = [_list_item(a, base, edition.timezone) for a in group]
        heading = ""
        if sectioned:
            name = escape(section or "Outras")
            anchor = _anchor(section or "Outras")
            heading = f'<h1 id="{anchor}">{name}</h1>\n'
            links.append(f'<a href="#{anchor}">{name}</a>')
        blocks.append(
            heading + '<ol class="articles">\n' + "\n".join(items) + "\n</ol>"
        )
    listing = "\n".join(blocks) or f"<p>{EMPTY[kind]}</p>"
    index = (
        f'<nav class="sections" aria-label="Seções">{" · ".join(links)}</nav>\n'
        if links
        else ""
    )
    label = _edition_label(entry)
    content = Template(_read("index.html")).substitute(
        tabs=_tabs(kind), heading=escape(label), sections=index, items=listing
    )
    menu = _menu(manifest, root, entry)
    return _page(f"{label} · Journal", content, root, menu)


def _tabs(current: str) -> str:
    links = [
        f'<a href="{LIST_PAGES[k]}"{' aria-current="page"' if k == current else ""}>'
        f"{label}</a>"
        for k, label in TABS.items()
    ]
    return (
        '<nav class="tabs" aria-label="Notícias ou artigos">'
        + "".join(links)
        + "</nav>"
    )


def _reading_time(body: str) -> str:
    """'12 min de leitura'; the body is markup the source rebuilt, so tags are clean."""
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return f"{max(1, round(words / WORDS_PER_MINUTE))} min de leitura"


def _anchor(name: str) -> str:
    """'Brasil e mundo' -> 'brasil-e-mundo': lowercase, no accents, hyphens."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "secao"


def _count(n: int) -> str:
    return f"{n} artigo" if n == 1 else f"{n} artigos"


def _list_item(a: Article, base: str, tz: tzinfo) -> str:
    w = _when(a, tz)
    summary = f'<p class="summary">{escape(a.summary)}</p>' if a.summary else ""
    # Nothing to show on the article page: go straight to the source.
    if a.summary or a.image:
        link = f'href="{base}articles/{a.id}.html"'
    else:
        link = f'href="{escape(a.url)}" rel="noopener noreferrer"'
    reading = f" · {_reading_time(a.body)}" if a.kind == "artigo" and a.body else ""
    return (
        f"<li>{_img(a, 'thumb')}"
        f"<h2><a {link}>{escape(a.title)}</a></h2>"
        f'<p class="meta">{escape(a.source)} · '
        f'<time datetime="{w["iso"]}">{w["date"]}</time>{reading}</p>{summary}</li>'
    )


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
    return _page("Edições · Journal", content, "../", _menu(manifest, "../", None))


def _article_page(
    a: Article, tz: tzinfo, root: str, manifest: list[dict], entry: dict
) -> str:
    content = Template(_read("article.html")).substitute(
        title=escape(a.title),
        source=escape(a.source),
        # the body is the only feed markup kept: the source rebuilt it already
        text=f'<div class="body">{a.body}</div>'
        if a.body
        else f"<p>{escape(a.summary)}</p>",
        url=escape(a.url),
        back=f"../{LIST_PAGES[a.kind]}",
        image=_figure(a),
        **_when(a, tz),
    )
    menu = _menu(manifest, root, entry)
    return _page(f"{a.title} · Journal", content, root, menu)


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
            "section": a.section,
            "kind": a.kind,
        }
        for a in articles
    ]
    return json.dumps(index, ensure_ascii=False, indent=2)
