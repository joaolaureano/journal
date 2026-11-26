from dataclasses import dataclass
from datetime import date

from journal.domain.article import Article


@dataclass(frozen=True)
class Edition:
    """One day's journal: the articles published for `date`, in display order."""

    date: date
    articles: tuple[Article, ...]
