from dataclasses import dataclass
from datetime import UTC, date, tzinfo

from journal.domain.article import Article


@dataclass(frozen=True)
class Edition:
    """One day's journal: the articles published for `date`, in display order
    (grouped by section). `timezone` is the one that decided the date; pages show
    times in it."""

    date: date
    articles: tuple[Article, ...]
    timezone: tzinfo = UTC
