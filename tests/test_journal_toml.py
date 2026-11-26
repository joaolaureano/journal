from pathlib import Path

from journal.config import load_config

CONFIG = Path(__file__).parent.parent / "journal.toml"


def test_journal_toml_is_valid():
    names = [s.name for s in load_config(CONFIG).sources]
    assert names
    assert len(names) == len(set(names))
