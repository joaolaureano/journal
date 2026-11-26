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
    assert "(0 already in earlier editions, 0 AI warm-ups)" in capsys.readouterr().out


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
