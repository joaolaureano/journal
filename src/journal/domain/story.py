import hashlib
from dataclasses import dataclass, field

from journal.domain.article import Article


@dataclass(frozen=True)
class Story:
    """One fact as several sources report it; `items[0]` leads."""

    items: tuple[Article, ...]
    section: str | None = None
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("a story needs at least one article")
        keys = "\n".join(sorted(a.key for a in self.items))
        object.__setattr__(self, "id", hashlib.sha256(keys.encode()).hexdigest()[:16])

    @property
    def lead(self) -> Article:
        return self.items[0]

    @property
    def sources(self) -> tuple[str, ...]:
        """Distinct source names, in item order."""
        return tuple(dict.fromkeys(a.source for a in self.items))
