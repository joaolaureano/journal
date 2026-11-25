import json
import shutil
from collections.abc import Sequence
from datetime import UTC
from html import escape
from importlib.resources import files
from pathlib import Path
from string import Template

from journal.domain import Article
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


class StaticSitePublisher:
    """Writes the whole site to `out_dir`, replacing a previous site as a unit."""

    def __init__(self, out_dir: str | Path):
        self.out_dir = Path(out_dir)

    def publish(self, articles: Sequence[Article]) -> None:
        out = self.out_dir.resolve()
        _check_replaceable(out)
        tmp, old = out.with_name(out.name + ".tmp"), out.with_name(out.name + ".old")
        _check_replaceable(tmp)
        _check_replaceable(old)
        try:
            shutil.rmtree(tmp, ignore_errors=True)
            _write_site(tmp, articles)
            if out.exists():
                shutil.rmtree(old, ignore_errors=True)
                out.rename(old)
            tmp.rename(out)
            shutil.rmtree(old, ignore_errors=True)
        except OSError as exc:
            shutil.rmtree(tmp, ignore_errors=True)
            raise PublishError(f"cannot publish to {out}: {exc}") from exc


def _check_replaceable(path: Path) -> None:
    """Only empty dirs or earlier journal sites may be replaced."""
    if not path.exists():
        return
    if path.is_dir() and (
        not any(path.iterdir()) or (path / "articles.json").is_file()
    ):
        return
    raise PublishError(f"refusing to replace {path}: not a journal site")


def _write_site(root: Path, articles: Sequence[Article]) -> None:
    (root / "articles").mkdir(parents=True)
    (root / "style.css").write_text(_read("style.css"), encoding="utf-8")
    (root / "articles.json").write_text(_index_json(articles), encoding="utf-8")
    (root / "index.html").write_text(_index_page(articles), encoding="utf-8")
    for article in articles:
        page = root / "articles" / f"{article.id}.html"
        page.write_text(_article_page(article), encoding="utf-8")


def _read(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _page(title: str, content: str, root: str) -> str:
    return Template(_read("base.html")).substitute(
        title=escape(title), content=content, root=root
    )


def _when(article: Article) -> dict[str, str]:
    d = article.published_at.astimezone(UTC)
    shown = f"{d.day} {MONTHS[d.month - 1]} {d.year}, {d:%H:%M} UTC"
    return {"iso": d.isoformat(), "date": shown}


def _index_page(articles: Sequence[Article]) -> str:
    items = []
    for a in articles:
        w = _when(a)
        summary = f'<p class="summary">{escape(a.summary)}</p>' if a.summary else ""
        items.append(
            f'<li><h2><a href="articles/{a.id}.html">{escape(a.title)}</a></h2>'
            f'<p class="meta">{escape(a.source)} · '
            f'<time datetime="{w["iso"]}">{w["date"]}</time></p>{summary}</li>'
        )
    listing = (
        '<ol class="articles">\n' + "\n".join(items) + "\n</ol>"
        if items
        else "<p>Nenhum artigo publicado.</p>"
    )
    content = Template(_read("index.html")).substitute(items=listing)
    return _page("Journal", content, root="")


def _article_page(a: Article) -> str:
    content = Template(_read("article.html")).substitute(
        title=escape(a.title),
        source=escape(a.source),
        summary=escape(a.summary),
        url=escape(a.url),
        **_when(a),
    )
    return _page(f"{a.title} · Journal", content, root="../")


def _index_json(articles: Sequence[Article]) -> str:
    index = [
        {
            "id": a.id,
            "title": a.title,
            "url": a.url,
            "summary": a.summary,
            "source": a.source,
            "published_at": a.published_at.isoformat(),
        }
        for a in articles
    ]
    return json.dumps(index, ensure_ascii=False, indent=2)
