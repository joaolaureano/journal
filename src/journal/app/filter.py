import re
import unicodedata
from collections.abc import Sequence
from urllib.parse import urlsplit

from journal.domain import Article


def normalize(text: str) -> str:
    """Casefolded, accent-free, single-spaced: 'Inflação  ALTA' -> 'inflacao alta'."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.casefold().split())


def _pattern(terms: Sequence[str]) -> re.Pattern[str] | None:
    if not terms:
        return None
    alternatives = "|".join(re.escape(normalize(t)) for t in terms)
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)")


class KeywordFilter:
    """Keeps articles mentioning an include term (if any) and no exclude term,
    whose link is not on an excluded domain (e.g. a paywalled outlet)."""

    def __init__(
        self,
        include: Sequence[str] = (),
        exclude: Sequence[str] = (),
        exclude_domains: Sequence[str] = (),
    ):
        self._include = _pattern(include)
        self._exclude = _pattern(exclude)
        self._domains = tuple(d.strip().lower().strip(".") for d in exclude_domains)

    def matches(self, article: Article) -> bool:
        host = (urlsplit(article.url).hostname or "").lower()
        if any(host == d or host.endswith(f".{d}") for d in self._domains):
            return False
        text = normalize(f"{article.title} {article.summary}")
        if self._exclude and self._exclude.search(text):
            return False
        return not self._include or bool(self._include.search(text))
