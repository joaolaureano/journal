from pathlib import Path

from journal.config import load_config

CONFIG = Path(__file__).parent.parent / "journal.toml"


def test_journal_toml_is_valid():
    sources = load_config(CONFIG).sources
    assert [s.name for s in sources] == ["Nature", "ScienceDaily"]
