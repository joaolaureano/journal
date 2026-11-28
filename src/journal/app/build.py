import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta, tzinfo

from journal.app.filter import KeywordFilter
from journal.domain import Article, Edition, Story, dedup_key
from journal.ports import (
    GrouperPort,
    HistoryPort,
    PublisherPort,
    SourceError,
    SourcePort,
    SummarizerPort,
    WriterPort,
)

__all__ = ["BuildError", "BuildJournal", "BuildReport", "dedup_key"]

FUTURE_TOLERANCE = timedelta(days=1)
WARMUP_WORKERS = 8
WARMUP_TIMEOUT = 180.0  # seconds for the whole step; the Lambda has 600
MAX_STORIES = 10
STORY_WORKERS = 4
STORY_TIMEOUT = 150.0  # seconds for writing every story


class BuildError(Exception):
    """No source delivered articles, so nothing was published."""


@dataclass
class BuildReport:
    edition: Edition
    errors: list[SourceError] = field(default_factory=list)
    fetched: int = 0  # unique articles read, before filtering
    already_published: int = 0  # dropped: published in an earlier day's edition
    warmup_errors: list[str] = field(default_factory=list)  # distinct messages
    story_errors: list[str] = field(default_factory=list)  # grouping failed: none

    @property
    def warmups(self) -> int:
        return sum(a.warmup is not None for a in self.edition.articles)

    @property
    def articles(self) -> list[Article]:
        return list(self.edition.articles)


class BuildJournal:
    def __init__(
        self,
        sources: Sequence[SourcePort],
        publisher: PublisherPort,
        article_filter: KeywordFilter | None = None,
        max_articles: int | None = None,
        max_age_days: int | None = None,
        max_per_section: int | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
        timezone: tzinfo = UTC,
        history: HistoryPort | None = None,
        summarizer: SummarizerPort | None = None,
        warmup_timeout: float = WARMUP_TIMEOUT,
        grouper: GrouperPort | None = None,
        max_stories: int = MAX_STORIES,
        writer: WriterPort | None = None,
        story_timeout: float = STORY_TIMEOUT,
    ):
        self.sources = sources
        self.publisher = publisher
        self.article_filter = article_filter
        self.max_articles = max_articles
        self.max_age_days = max_age_days
        self.max_per_section = max_per_section
        self.now = now
        self.timezone = timezone  # decides which day an edition belongs to
        self.history = history  # what earlier editions already published
        self.summarizer = summarizer  # writes the articles' warm-up paragraph
        self.warmup_timeout = warmup_timeout
        self.grouper = grouper  # finds items about the same fact
        self.max_stories = max_stories
        self.writer = writer  # writes each kept story from its items
        self.story_timeout = story_timeout

    def run(self) -> BuildReport:
        by_url: dict[str, Article] = {}
        errors: list[SourceError] = []
        succeeded = 0
        for source in self.sources:
            try:
                fetched = source.fetch()
            except SourceError as exc:
                errors.append(exc)
                continue
            except Exception as exc:  # a buggy adapter must not sink the others
                name = getattr(source, "name", type(source).__name__)
                error = SourceError(f"unexpected error in source {name}: {exc!r}")
                error.__cause__ = exc
                errors.append(error)
                continue
            succeeded += 1
            for article in fetched:
                by_url.setdefault(article.key, article)
        if not succeeded:
            raise BuildError(
                "no source fetched successfully: "
                + ("; ".join(map(str, errors)) or "no sources configured")
            )
        day = self.now().astimezone(self.timezone).date()
        seen = self.history.published_before(day) if self.history else set()
        fresh = {k: a for k, a in by_url.items() if k not in seen}
        kept = [
            a
            for a in fresh.values()
            if self._in_window(a)
            and (not self.article_filter or self.article_filter.matches(a))
        ]
        articles = sorted(kept, key=lambda a: (-a.published_at.timestamp(), a.url))
        # sections in the order their first source was configured; others last
        order = list(dict.fromkeys(getattr(s, "section", None) for s in self.sources))
        rank = {name: i for i, name in enumerate(n for n in order if n is not None)}
        # stories see every candidate: the per-section cap is for the news list only
        stories, story_errors = self._stories(
            [a for a in articles if a.kind == "noticia"], rank
        )
        stories, write_errors = self._write(stories)
        story_errors += write_errors
        if self.max_per_section is not None:
            articles = _cap_per_section(articles, self.max_per_section)
        articles = articles[: self.max_articles]
        articles.sort(key=lambda a: rank.get(a.section, len(rank)))  # stable
        articles, warmup_errors = self._warm_up(articles)
        edition = Edition(day, tuple(articles), self.timezone, tuple(stories))
        self.publisher.publish(edition)
        return BuildReport(
            edition,
            errors,
            fetched=len(by_url),
            already_published=len(by_url) - len(fresh),
            warmup_errors=warmup_errors,
            story_errors=story_errors,
        )

    def _stories(
        self, news: list[Article], rank: dict[str, int]
    ) -> tuple[list[Story], list[str]]:
        """The day's stories, best covered first; a grouper failure gives none."""
        if self.grouper is None or not news:
            return [], []
        try:
            groups = [_coherent(g) for g in self.grouper.group(news)]
        except Exception as exc:  # any adapter failure only costs the stories
            return [], [str(exc) or repr(exc)]
        candidates = {a.key for a in news}
        taken: set[str] = set()
        sets: list[list[Article]] = []
        for group in [*groups, *([a] for a in news)]:  # leftovers stand alone
            items = []
            for a in group:
                if a.key in candidates and a.key not in taken:
                    taken.add(a.key)
                    items.append(a)
            if items:
                sets.append(items)
        sources = {getattr(s, "name", None): i for i, s in enumerate(self.sources)}
        ranked = sorted((_story(items, rank, sources) for items in sets), key=_coverage)
        best: dict[str | None, Story] = {}
        for story in ranked:
            best.setdefault(story.section, story)
        firsts = sorted(best.values(), key=lambda s: rank.get(s.section, len(rank)))
        chosen = {s.id for s in firsts[: self.max_stories]}
        for story in ranked:
            if len(chosen) >= self.max_stories:
                break
            chosen.add(story.id)
        return [s for s in ranked if s.id in chosen], []

    def _write(self, stories: list[Story]) -> tuple[list[Story], list[str]]:
        """Adds the writer's text to each story; failures only leave it without."""
        if self.writer is None or not stories:
            return stories, []
        pool = ThreadPoolExecutor(STORY_WORKERS)
        futures = {pool.submit(self.writer.write, s): s for s in stories}
        done, pending = wait(futures, timeout=self.story_timeout)
        pool.shutdown(wait=False, cancel_futures=True)  # late answers are dropped
        texts, errors = {}, []
        for future in done:
            try:
                text = future.result()
            except Exception as exc:  # any adapter failure only costs this text
                errors.append(str(exc) or repr(exc))
                continue
            if text:
                texts[futures[future].id] = text
        if pending:
            errors.append(
                f"story writing timed out: {len(pending)} stories without text"
            )
        written = []
        for story in stories:
            if story.id in texts:
                try:
                    story = replace(story, text=texts[story.id])
                except ValueError as exc:  # cites items outside the story
                    errors.append(f"invalid story text: {exc}")
            written.append(story)
        return written, list(dict.fromkeys(errors))

    def _warm_up(self, articles: list[Article]) -> tuple[list[Article], list[str]]:
        """Adds the summarizer's warm-up to each `artigo`; failures only skip it."""
        targets = [a for a in articles if a.kind == "artigo"]
        if self.summarizer is None or not targets:
            return articles, []
        pool = ThreadPoolExecutor(WARMUP_WORKERS)
        futures = {pool.submit(self.summarizer.warmup, a): a for a in targets}
        done, pending = wait(futures, timeout=self.warmup_timeout)
        pool.shutdown(wait=False, cancel_futures=True)  # late calls are dropped
        texts, errors = {}, []
        for future in done:
            try:
                text = future.result()
            except Exception as exc:  # any adapter failure only skips this item
                errors.append(str(exc) or repr(exc))
                continue
            if text:
                texts[futures[future].key] = text
        if pending:
            errors.append(f"warm-up timed out: {len(pending)} articles without it")
        warmed = [
            replace(a, warmup=texts[a.key]) if a.key in texts else a for a in articles
        ]
        return warmed, list(dict.fromkeys(errors))

    def _in_window(self, article: Article) -> bool:
        """Drops stale articles and ones dated implausibly far in the future."""
        now = self.now()
        if article.published_at > now + FUTURE_TOLERANCE:
            return False
        if self.max_age_days is None or article.evergreen:
            return True
        return article.published_at >= now - timedelta(days=self.max_age_days)


STOP_WORDS = set(
    "para pelo pela pelos pelas sobre apos entre como mais veja nesta neste nessa "
    "nesse essa esse isso quando onde depois ainda tambem seus suas pode sera esta "
    "estao foram quem qual contra diz dizem afirma".split()
)


def _words(title: str) -> set[str]:
    """Lowercase words of four letters or more, without accents or stop words."""
    plain = unicodedata.normalize("NFKD", title)
    plain = "".join(c for c in plain if not unicodedata.combining(c)).casefold()
    return {w for w in re.findall(r"\w+", plain) if len(w) > 3} - STOP_WORDS


def _coherent(group: list[Article]) -> list[Article]:
    """The group without items whose title shares no word with the others' (with
    two of them, in groups of four or more): the grouper sometimes adds a different
    fact. Dropped items stand alone."""
    words = [_words(a.title) for a in group]
    need = 2 if len(group) >= 4 else 1
    kept = []
    for i, a in enumerate(group):
        others = Counter(w for j, ws in enumerate(words) if j != i for w in ws)
        if any(others[w] >= need for w in words[i]):
            kept.append(a)
    return kept


def _story(items: list[Article], rank: dict[str, int], sources: dict) -> Story:
    """Lead: newest item of the source configured first. Section: the lead's, so a
    regional section configured last keeps only stories no other section covered."""
    items.sort(
        key=lambda a: (sources.get(a.source, len(sources)), -a.published_at.timestamp())
    )
    return Story(tuple(items), items[0].section)


def _coverage(story: Story) -> tuple[int, float]:
    """More distinct sources first, then the story with the newest item."""
    return (-len(story.sources), -max(a.published_at.timestamp() for a in story.items))


def _cap_per_section(articles: list[Article], limit: int) -> list[Article]:
    """Keeps the first `limit` articles of each section and kind, preserving order."""
    counts: dict[tuple[str | None, str], int] = {}
    kept = []
    for a in articles:
        key = (a.section, a.kind)  # news and articles of a section count apart
        counts[key] = counts.get(key, 0) + 1
        if counts[key] <= limit:
            kept.append(a)
    return kept
