import hashlib
from dataclasses import dataclass, field

from journal.domain.article import Article


@dataclass(frozen=True)
class Paragraph:
    """Plain text and the ids of the story items that support it."""

    text: str
    sources: tuple[str, ...]


@dataclass(frozen=True)
class Divergence:
    """A point the items disagree on: (item id, what that item says) per version."""

    point: str
    views: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class StoryText:
    """A story written by a language model, in plain text, from its items only."""

    title: str
    paragraphs: tuple[Paragraph, ...]
    divergences: tuple[Divergence, ...] = ()


@dataclass(frozen=True)
class Story:
    """One fact as several sources report it; `items[0]` leads."""

    items: tuple[Article, ...]
    section: str | None = None
    text: StoryText | None = None
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("a story needs at least one article")
        keys = "\n".join(sorted(a.key for a in self.items))
        object.__setattr__(self, "id", hashlib.sha256(keys.encode()).hexdigest()[:16])
        if self.text is not None:
            _check(self.text, {a.id for a in self.items})

    @property
    def lead(self) -> Article:
        return self.items[0]

    @property
    def sources(self) -> tuple[str, ...]:
        """Distinct source names, in item order."""
        return tuple(dict.fromkeys(a.source for a in self.items))

    def item(self, article_id: str) -> Article:
        return next(a for a in self.items if a.id == article_id)


def _check(text: StoryText, ids: set[str]) -> None:
    """Every claim rests on the story's own items: no other source is ever credited."""
    if not text.title.strip() or not text.paragraphs:
        raise ValueError("a story text needs a title and a paragraph")
    for p in text.paragraphs:
        if not p.text.strip() or not p.sources or not set(p.sources) <= ids:
            raise ValueError("every paragraph must cite items of its story")
    for d in text.divergences:
        cited = {item for item, _ in d.views}
        if not d.point.strip() or len(cited) < 2 or not cited <= ids:
            raise ValueError("a divergence needs versions from two items of its story")
