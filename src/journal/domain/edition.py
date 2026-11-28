from dataclasses import dataclass
from datetime import UTC, date, tzinfo

from journal.domain.article import Article
from journal.domain.story import Story


@dataclass(frozen=True)
class Edition:
    """One day's journal: the articles published for `date`, in display order
    (grouped by section), and the stories chosen from them. `timezone` is the one
    that decided the date; pages show times in it."""

    date: date
    articles: tuple[Article, ...]
    timezone: tzinfo = UTC
    stories: tuple[Story, ...] = ()  # the day's stories, in display order
