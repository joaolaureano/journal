from importlib.metadata import EntryPoint, EntryPoints
from pathlib import Path

import pytest
from fakes import FakeSource, article

from journal import config
from journal.adapters.rss import RssSource
from journal.adapters.static_site import StaticSitePublisher
from journal.config import AdapterType, ConfigError, load_config

PUBLISHER = '[publisher]\ntype = "static-site"\n'
RSS = '[[sources]]\ntype = "rss"\nname = "{name}"\nurl = "{url}"\n'


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "journal.toml"
    path.write_text(text, encoding="utf-8")
    return path


def rss(name="Nature", url="https://www.nature.com/nature.rss", extra=""):
    return RSS.format(name=name, url=url) + extra


def test_two_sources_in_order_and_publisher(tmp_path):
    cfg = load_config(
        write(
            tmp_path,
            rss("A", "https://a.com/feed") + rss("B", "https://b.com/feed") + PUBLISHER,
        )
    )
    assert [type(s) for s in cfg.sources] == [RssSource, RssSource]
    assert [s.name for s in cfg.sources] == ["A", "B"]
    assert isinstance(cfg.publisher, StaticSitePublisher)


def test_rss_source_options(tmp_path):
    cfg = load_config(write(tmp_path, rss(extra="timeout = 3\n") + PUBLISHER))
    source = cfg.sources[0]
    assert (source.location, source.name, source.timeout) == (
        "https://www.nature.com/nature.rss",
        "Nature",
        3,
    )


def test_rss_timeout_defaults_to_10(tmp_path):
    assert load_config(write(tmp_path, rss() + PUBLISHER)).sources[0].timeout == 10


def test_relative_out_resolved_against_config_dir(tmp_path, monkeypatch):
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.chdir(tmp_path)
    path = site / "journal.toml"
    path.write_text(rss() + PUBLISHER + 'out = "public"\n')
    assert load_config(path).publisher.storage.root == site.resolve() / "public"


def test_out_defaults_to_dist(tmp_path):
    publisher = load_config(write(tmp_path, rss() + PUBLISHER)).publisher
    assert publisher.storage.root == tmp_path.resolve() / "dist"


def test_registered_source_type_is_usable(tmp_path, monkeypatch):
    fake = FakeSource([])
    monkeypatch.setitem(
        config.SOURCE_TYPES,
        "fake",
        AdapterType(build=lambda options, _dir: fake, required={"label": str}),
    )
    text = '[[sources]]\ntype = "fake"\nlabel = "x"\n' + PUBLISHER
    assert load_config(write(tmp_path, text)).sources == [fake]


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("sources = [\n", "invalid TOML"),
        (PUBLISHER, "sources"),
        ("sources = []\n" + PUBLISHER, "sources"),
        (rss(), "publisher"),
        (
            '[[sources]]\ntype = "carrier-pigeon"\n' + PUBLISHER,
            r"source #1: unknown type 'carrier-pigeon' \(known: rss\)",
        ),
        (
            rss() + '[[sources]]\ntype = "rss"\nname = "x"\n' + PUBLISHER,
            r"source #2.*'url'",
        ),
        (rss(extra='ulr = "x"\n') + PUBLISHER, "'ulr'"),
        (rss(extra='timeout = "fast"\n') + PUBLISHER, "'timeout'"),
        (rss(extra="timeout = true\n") + PUBLISHER, "'timeout'"),
        (rss() + '[publisher]\ntype = "ftp"\n', "publisher: unknown type 'ftp'"),
    ],
    ids=[
        "invalid-toml",
        "no-sources",
        "empty-sources",
        "no-publisher",
        "unknown-type",
        "missing-option",
        "unknown-option",
        "wrong-type",
        "bool-is-not-a-number",
        "unknown-publisher-type",
    ],
)
def test_invalid_configuration_rejected(tmp_path, text, message):
    with pytest.raises(ConfigError, match=message):
        load_config(write(tmp_path, text))


def test_missing_file_rejected(tmp_path):
    with pytest.raises(ConfigError, match="nope.toml"):
        load_config(tmp_path / "nope.toml")


# plugins (entry points)


def plugins(monkeypatch, *declared):
    """Pretend the given (name, value, group) entry points are installed."""
    installed = EntryPoints(EntryPoint(n, v, g) for n, v, g in declared)
    monkeypatch.setattr(config, "entry_points", lambda **p: installed.select(**p))


FAKE_SOURCE = '[[sources]]\ntype = "fake"\nurl = "https://plugin.example/a"\n'


def test_plugin_source_type_used_like_builtin(tmp_path, monkeypatch):
    plugins(monkeypatch, ("fake", "sample_plugin:FAKE", "journal.sources"))
    source = load_config(write(tmp_path, FAKE_SOURCE + PUBLISHER)).sources[0]
    assert [a.url for a in source.fetch()] == ["https://plugin.example/a"]


def test_plugin_types_listed_as_known(tmp_path, monkeypatch):
    plugins(monkeypatch, ("fake", "sample_plugin:FAKE", "journal.sources"))
    text = '[[sources]]\ntype = "nope"\n' + PUBLISHER
    with pytest.raises(ConfigError, match=r"known: fake, rss"):
        load_config(write(tmp_path, text))


def test_unused_broken_plugin_is_ignored(tmp_path, monkeypatch):
    plugins(monkeypatch, ("broken", "no_such_module:X", "journal.sources"))
    assert load_config(write(tmp_path, rss() + PUBLISHER)).sources


def test_used_broken_plugin_rejected(tmp_path, monkeypatch):
    plugins(monkeypatch, ("broken", "no_such_module:X", "journal.sources"))
    text = '[[sources]]\ntype = "broken"\n' + PUBLISHER
    with pytest.raises(ConfigError, match=r"'broken' \(no_such_module:X\)"):
        load_config(write(tmp_path, text))


def test_entry_point_not_an_adapter_type_rejected(tmp_path, monkeypatch):
    plugins(monkeypatch, ("odd", "sample_plugin:NOT_AN_ADAPTER", "journal.sources"))
    text = '[[sources]]\ntype = "odd"\n' + PUBLISHER
    with pytest.raises(ConfigError, match="'odd'.*not an AdapterType"):
        load_config(write(tmp_path, text))


def test_plugin_reusing_builtin_name_is_ambiguous(tmp_path, monkeypatch):
    plugins(monkeypatch, ("rss", "sample_plugin:FAKE", "journal.sources"))
    with pytest.raises(ConfigError, match="built-in, sample_plugin:FAKE"):
        load_config(write(tmp_path, rss() + PUBLISHER))


def test_non_string_type_rejected(tmp_path):
    text = "[[sources]]\ntype = [1]\n" + PUBLISHER
    with pytest.raises(ConfigError, match="'type' must be a string"):
        load_config(write(tmp_path, text))


# [filter]


def test_no_filter_by_default(tmp_path):
    cfg = load_config(write(tmp_path, rss() + PUBLISHER))
    assert cfg.article_filter is None and cfg.max_articles is None


def test_filter_from_configuration(tmp_path):
    text = rss() + PUBLISHER + '[filter]\ninclude = ["selic"]\nmax_articles = 5\n'
    cfg = load_config(write(tmp_path, text))
    assert cfg.max_articles == 5
    assert cfg.max_age_days is None
    assert cfg.article_filter.matches(article(title="Copom mantém a Selic"))
    assert not cfg.article_filter.matches(article(title="Futebol"))


@pytest.mark.parametrize(
    "table, key",
    [
        ("max_articles = 0", "max_articles"),
        ("max_age_days = 0", "max_age_days"),
        ("max_age_days = 1.5", "max_age_days"),
        ("max_articles = true", "max_articles"),
        ('max_articles = "5"', "max_articles"),
        ('include = "selic"', "include"),
        ('include = [""]', "include"),
        ("exclude = [1]", "exclude"),
        ('inclde = ["selic"]', "inclde"),
    ],
)
def test_invalid_filter_rejected(tmp_path, table, key):
    with pytest.raises(ConfigError, match=key):
        load_config(write(tmp_path, rss() + PUBLISHER + f"[filter]\n{table}\n"))


def test_max_age_days_from_configuration(tmp_path):
    cfg = load_config(
        write(tmp_path, rss() + PUBLISHER + "[filter]\nmax_age_days = 2\n")
    )
    assert cfg.max_age_days == 2


def test_filter_must_be_table(tmp_path):
    with pytest.raises(ConfigError, match=r"\[filter\]"):
        load_config(write(tmp_path, 'filter = "selic"\n' + rss() + PUBLISHER))


# storage and timezone


def test_storage_table_selects_local_out(tmp_path):
    text = rss() + PUBLISHER + 'storage = { type = "local", out = "site" }\n'
    assert load_config(write(tmp_path, text)).publisher.storage.root == (
        tmp_path.resolve() / "site"
    )


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ('out = "a"\nstorage = { type = "local" }\n', "either 'out' or 'storage'"),
        ('storage = { type = "ftp" }\n', "storage: unknown type 'ftp'"),
        ('storage = { type = "local", dir = "x" }\n', "'dir'"),
        ('storage = "local"\n', "'storage'"),
    ],
)
def test_invalid_storage_rejected(tmp_path, extra, message):
    with pytest.raises(ConfigError, match=message):
        load_config(write(tmp_path, rss() + PUBLISHER + extra))


def test_timezone_defaults_to_sao_paulo(tmp_path):
    assert str(load_config(write(tmp_path, rss() + PUBLISHER)).timezone) == (
        "America/Sao_Paulo"
    )


def test_timezone_from_configuration(tmp_path):
    text = 'timezone = "Europe/Lisbon"\n' + rss() + PUBLISHER
    assert str(load_config(write(tmp_path, text)).timezone) == "Europe/Lisbon"


@pytest.mark.parametrize("value", ['"Mars/Olympus"', "3"])
def test_invalid_timezone_rejected(tmp_path, value):
    with pytest.raises(ConfigError, match="timezone"):
        load_config(write(tmp_path, f"timezone = {value}\n" + rss() + PUBLISHER))
