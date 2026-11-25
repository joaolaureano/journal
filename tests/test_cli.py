import json
from pathlib import Path

from journal.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def config(tmp_path, *feeds, out="dist"):
    sources = "".join(
        f'[[sources]]\ntype = "rss"\nname = "{name}"\nurl = "{url}"\n'
        for name, url in feeds
    )
    path = tmp_path / "journal.toml"
    path.write_text(sources + f'[publisher]\ntype = "static-site"\nout = "{out}"\n')
    return str(path)


def test_build_from_two_sources(tmp_path, capsys):
    path = config(
        tmp_path,
        ("One", (FIXTURES / "feed.xml").as_uri()),
        ("Two", (FIXTURES / "feed2.xml").as_uri()),
    )
    code = main(["build", "--config", path])
    index = json.loads((tmp_path / "dist" / "articles.json").read_text("utf-8"))
    assert code == 0
    assert {a["source"] for a in index} == {"One", "Two"}
    assert [a["url"] for a in index].count("https://example.com/first") == 1
    assert f"published {len(index)} articles" in capsys.readouterr().out


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
