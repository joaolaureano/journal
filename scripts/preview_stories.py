"""Local preview of an edition with stories, without calling DeepSeek.

Stand-ins replace the LLM: stories group items whose titles share words, and each
story's "text" is one paragraph per item taken from that item's own summary. Good
enough to see the layout with real feeds; not a measure of the real grouping.

    sed 's|out = "dist"|out = "site"|' journal.toml > /tmp/preview/journal.toml
    env -u DEEPSEEK_API_KEY uv run python scripts/preview_stories.py \
        /tmp/preview/journal.toml
    open /tmp/preview/site/index.html
"""

import re
import sys
import unicodedata

from journal import cli
from journal.config import load_config
from journal.domain import Divergence, Paragraph, StoryText

STOP = set(
    "a o as os de da do das dos e em no na nos nas um uma para por com que se".split()
)


def words(title: str) -> set[str]:
    plain = unicodedata.normalize("NFKD", title)
    plain = "".join(c for c in plain if not unicodedata.combining(c)).casefold()
    return {w for w in re.findall(r"\w+", plain) if len(w) > 3 and w not in STOP}


class OverlapGrouper:
    """Same fact = items from other sources sharing three title words."""

    def group(self, articles):
        ws = [words(a.title) for a in articles]
        groups, used = [], set()
        for i, a in enumerate(articles):
            if i in used:
                continue
            group = [i] + [
                j
                for j in range(i + 1, len(articles))
                if j not in used
                and articles[j].source != a.source
                and len(ws[i] & ws[j]) >= 3
            ]
            if len(group) > 1:
                used.update(group)
                groups.append([articles[k] for k in group])
        return groups


class EchoWriter:
    """One paragraph per item, from its own summary; a sample divergence."""

    def write(self, story):
        paragraphs = tuple(
            Paragraph(a.summary or a.title, (a.id,)) for a in story.items[:4]
        )
        divergences = ()
        if len(story.items) > 1:
            a, b = story.items[:2]
            views = ((a.id, a.title[:80]), (b.id, b.title[:80]))
            divergences = (Divergence("Exemplo de divergência", views),)
        return StoryText(f"[prévia] {story.lead.title}", paragraphs, divergences)


def main(path: str) -> None:
    config = load_config(path)
    config.stories = config.stories or {"max_stories": 10}
    cli.grouper = lambda c: OverlapGrouper()
    cli.writer = lambda c, cache=None: EchoWriter()
    print(cli.summary(cli.run(config)))


if __name__ == "__main__":
    main(sys.argv[1])
