import json
from pathlib import Path

from journal.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def config(tmp_path, *feeds, out="dist", extra=""):
    sources = "".join(
        f'[[sources]]\ntype = "rss"\nname = "{name}"\nurl = "{url}"\n'
        for name, url in feeds
    )
    path = tmp_path / "journal.toml"
    path.write_text(
        sources + f'[publisher]\ntype = "static-site"\nout = "{out}"\n' + extra
    )
    return str(path)


def latest_articles(out: Path) -> list[dict]:
    manifest = json.loads((out / "editions.json").read_text("utf-8"))
    return json.loads((out / manifest[-1]["path"] / "articles.json").read_text("utf-8"))


def test_build_from_two_sources(tmp_path, capsys):
    path = config(
        tmp_path,
        ("One", (FIXTURES / "feed.xml").as_uri()),
        ("Two", (FIXTURES / "feed2.xml").as_uri()),
    )
    code = main(["build", "--config", path])
    index = latest_articles(tmp_path / "dist")
    assert code == 0
    assert {a["source"] for a in index} == {"One", "Two"}
    assert [a["url"] for a in index].count("https://example.com/first") == 1
    assert f"published {len(index)} of {len(index)} articles" in capsys.readouterr().out


def test_failing_feed_exits_non_zero_without_output(tmp_path, capsys):
    path = config(tmp_path, ("X", (tmp_path / "missing.xml").as_uri()))
    assert main(["build", "--config", path]) != 0
    assert "missing.xml" in capsys.readouterr().err
    assert not (tmp_path / "dist").exists()


def test_publish_failure_exits_non_zero(tmp_path, capsys):
    (tmp_path / "notes.txt").write_text("keep")
    path = config(tmp_path, ("X", (FIXTURES / "feed.xml").as_uri()), out=".")
    assert main(["build", "--config", path]) != 0
    assert "refusing" in capsys.readouterr().err
    assert (tmp_path / "notes.txt").read_text() == "keep"


def test_invalid_config_exits_non_zero_without_output(tmp_path, capsys):
    path = tmp_path / "journal.toml"
    path.write_text(
        '[[sources]]\ntype = "carrier-pigeon"\n[publisher]\ntype = "static-site"\n'
    )
    assert main(["build", "--config", str(path)]) != 0
    assert "carrier-pigeon" in capsys.readouterr().err
    assert not (tmp_path / "dist").exists()


def test_missing_config_exits_non_zero(tmp_path, capsys):
    assert main(["build", "--config", str(tmp_path / "nope.toml")]) != 0
    assert "nope.toml" in capsys.readouterr().err


def test_build_applies_filter_cap(tmp_path, capsys):
    path = config(
        tmp_path,
        ("One", (FIXTURES / "feed.xml").as_uri()),
        extra="[filter]\nmax_articles = 1\n",
    )
    assert main(["build", "--config", path]) == 0
    index = latest_articles(tmp_path / "dist")
    assert len(index) == 1
    assert "published 1 of " in capsys.readouterr().out


def test_second_build_same_day_adds_a_revision(tmp_path, capsys):
    path = config(tmp_path, ("One", (FIXTURES / "feed.xml").as_uri()))
    assert main(["build", "--config", path]) == 0
    assert main(["build", "--config", path]) == 0
    manifest = json.loads((tmp_path / "dist" / "editions.json").read_text("utf-8"))
    assert [e["revision"] for e in manifest] == [1, 2]
    assert [e["articles"] for e in manifest][0] == manifest[1]["articles"] > 0
    assert (
        "(0 already in earlier editions, 0 AI warm-ups, 0 stories, 0 written)"
        in capsys.readouterr().out
    )


def test_summarizer_needs_the_api_key(tmp_path, monkeypatch, capsys):
    from journal.cli import summarizer
    from journal.config import load_config

    path = config(tmp_path, ("One", (FIXTURES / "feed.xml").as_uri()))
    with open(path, "a", encoding="utf-8") as f:
        f.write("[summarizer]\nmax_calls = 3\ntimeout = 9\n")
    cfg = load_config(path)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    assert summarizer(cfg) is None
    assert "DEEPSEEK_API_KEY is not set" in capsys.readouterr().err
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    s = summarizer(cfg, cache="storage")
    assert (s.api_key, s.cache, s._calls_left) == ("k", "storage", 3)


def write_feed(path: Path, *items: tuple[str, int]) -> str:
    """RSS file with (slug, hours ago) items, dated from now so the pool keeps them."""
    from datetime import UTC, datetime, timedelta
    from email.utils import format_datetime

    now = datetime.now(UTC)
    entries = "".join(
        f"<item><title>{slug}</title><link>https://example.com/{slug}</link>"
        f"<description>{slug}</description>"
        f"<pubDate>{format_datetime(now - timedelta(hours=age))}</pubDate></item>"
        for slug, age in items
    )
    path.write_text(
        f'<?xml version="1.0"?><rss version="2.0"><channel>{entries}</channel></rss>'
    )
    return path.as_uri()


def pooled_config(tmp_path, url, section):
    path = tmp_path / "journal.toml"
    path.write_text(
        f'[[sources]]\ntype = "rss"\nname = "Feed"\nurl = "{url}"\n'
        f'section = "{section}"\n'
        '[publisher]\ntype = "static-site"\nout = "dist"\n[pool]\n'
    )
    return str(path)


def test_collect_fills_the_pool_without_publishing(tmp_path, capsys):
    url = write_feed(tmp_path / "feed.xml", ("early", 3))
    assert main(["collect", "--config", pooled_config(tmp_path, url, "S1")]) == 0
    out = tmp_path / "dist"
    assert len(list((out / "pool").iterdir())) == 1
    assert not (out / "editions.json").exists() and not (out / "index.html").exists()
    assert "collected 1 articles from 1 of 1 sources" in capsys.readouterr().out


def test_build_gets_what_left_the_feed_with_the_current_section(tmp_path):
    feed = tmp_path / "feed.xml"
    url = write_feed(feed, ("early", 3))
    assert main(["collect", "--config", pooled_config(tmp_path, url, "Old")]) == 0
    write_feed(feed, ("late", 1))  # "early" is gone from the feed
    assert main(["build", "--config", pooled_config(tmp_path, url, "New")]) == 0
    index = latest_articles(tmp_path / "dist")
    assert sorted((a["title"], a["section"]) for a in index) == [
        ("early", "New"),
        ("late", "New"),
    ]


def test_collect_without_pool_fails_and_fetches_nothing(tmp_path, capsys):
    path = config(tmp_path, ("X", (tmp_path / "missing.xml").as_uri()))
    assert main(["collect", "--config", path]) != 0
    err = capsys.readouterr().err
    assert "[pool] is not configured" in err and "missing.xml" not in err
    assert not (tmp_path / "dist").exists()


def test_collect_fails_when_no_source_answers(tmp_path, capsys):
    path = pooled_config(tmp_path, (tmp_path / "missing.xml").as_uri(), "S")
    assert main(["collect", "--config", path]) != 0
    assert "no source fetched successfully" in capsys.readouterr().err


def test_stories_need_the_key(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    path = config(
        tmp_path, ("One", (FIXTURES / "feed.xml").as_uri()), extra="[stories]\n"
    )
    assert main(["build", "--config", path]) == 0
    captured = capsys.readouterr()
    assert "stories skipped: DEEPSEEK_API_KEY is not set" in captured.err
    assert "0 stories" in captured.out


def test_stories_from_the_configured_grouper(tmp_path, monkeypatch, capsys):
    from fakes import FakeGrouper

    from journal import cli

    made = {}

    def fake(key, **options):
        made.update(options, key=key)
        return FakeGrouper(["https://example.com/first", "https://example.com/second"])

    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setattr(cli, "DeepSeekGrouper", fake)
    extra = '[stories]\nmax_stories = 2\nmodel = "m"\n'
    path = config(tmp_path, ("One", (FIXTURES / "feed.xml").as_uri()), extra=extra)
    assert main(["build", "--config", path]) == 0
    assert made == {"key": "k", "model": "m"}
    assert "2 stories" in capsys.readouterr().out


def test_stories_are_written_with_the_configured_writer(tmp_path, monkeypatch, capsys):
    from fakes import FakeGrouper, FakeWriter

    from journal import cli

    made = {}

    def fake_writer(key, cache, **options):
        made.update(options, key=key, cache=cache)
        return FakeWriter()

    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setattr(cli, "DeepSeekGrouper", lambda key, **o: FakeGrouper())
    monkeypatch.setattr(cli, "DeepSeekWriter", fake_writer)
    extra = "[stories]\nmax_stories = 2\nmax_calls = 3\n"
    path = config(tmp_path, ("One", (FIXTURES / "feed.xml").as_uri()), extra=extra)
    assert main(["build", "--config", path]) == 0
    assert made["key"] == "k" and made["max_calls"] == 3 and made["cache"] is not None
    assert "2 stories, 2 written" in capsys.readouterr().out
