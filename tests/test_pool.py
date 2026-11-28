import json
from datetime import UTC, datetime, timedelta

import pytest
from fakes import FakeSource, article

from journal.adapters.pool import MAX_ITEMS, Pooled
from journal.adapters.storage import LocalStorage
from journal.ports import SourceError

NOW = datetime(2026, 11, 30, 11, 0, tzinfo=UTC)  # 08:00 in São Paulo


class MemoryStorage:
    def __init__(self, fail_read: bool = False, fail_write: bool = False):
        self.files: dict[str, bytes] = {}
        self.fail_read, self.fail_write = fail_read, fail_write

    def exists(self, key):
        return key in self.files

    def read(self, key):
        if self.fail_read:
            raise OSError("read failed")
        return self.files.get(key)

    def write(self, key, data):
        if self.fail_write:
            raise OSError("write failed")
        self.files[key] = data


class DownSource:
    name = "down"

    def fetch(self):
        raise SourceError("feed down")


def pooled(source, storage, now=NOW, hours=48):
    source.name = getattr(source, "name", "fake")
    return Pooled(source, storage, hours, now=lambda: now)


def at(hours_ago: float):
    return NOW - timedelta(hours=hours_ago)


def test_item_that_left_the_feed_is_still_returned():
    storage = MemoryStorage()
    early = article("https://a.com/1", published_at=at(5))
    pooled(FakeSource([early]), storage, now=at(4.5)).fetch()  # 03:30 collection
    later = article("https://a.com/2", published_at=at(1))
    got = pooled(FakeSource([later]), storage).fetch()
    assert {a.url for a in got} == {"https://a.com/1", "https://a.com/2"}


def test_item_outside_the_window_is_dropped():
    storage = MemoryStorage()
    old = article("https://a.com/old", published_at=at(50))
    pooled(FakeSource([old]), storage, now=at(10)).fetch()  # stored at 40 h old
    got = pooled(FakeSource([]), storage).fetch()
    assert got == []
    assert json.loads(next(iter(storage.files.values())))["articles"] == []


def test_feed_version_wins_over_stored_one():
    storage = MemoryStorage()
    url = "https://a.com/1"
    pooled(FakeSource([article(url, title="Old", published_at=at(2))]), storage).fetch()
    new = article(url, title="New", published_at=at(2))
    got = pooled(FakeSource([new]), storage).fetch()
    assert [a.title for a in got] == ["New"]


def test_round_trip_keeps_every_field():
    storage = MemoryStorage()
    full = article(
        "https://a.com/1",
        published_at=at(1),
        image="https://a.com/i.jpg",
        image_caption="c",
        image_credit="cr",
        body="<p>b</p>",
        kind="artigo",
        section="S",
    )
    pooled(FakeSource([full]), storage).fetch()
    assert pooled(FakeSource([]), storage).fetch() == [full]


def test_corrupt_entry_counts_as_empty_and_is_replaced():
    storage = MemoryStorage()
    source = FakeSource([article("https://a.com/1", published_at=at(1))])
    p = pooled(source, storage)
    storage.files[p.key] = b"not json"
    assert [a.url for a in p.fetch()] == ["https://a.com/1"]
    assert json.loads(storage.files[p.key])["articles"][0]["url"] == "https://a.com/1"


def test_bad_item_and_foreign_entry_are_skipped():
    storage = MemoryStorage()
    p = pooled(FakeSource([]), storage)
    good = {
        "title": "T",
        "url": "https://a.com/1",
        "summary": "",
        "source": "fake",
        "published_at": at(1).isoformat(),
    }
    storage.files[p.key] = json.dumps(
        {"source": "fake", "articles": [good, {"title": "", "url": "x"}]}
    ).encode()
    assert [a.url for a in p.fetch()] == ["https://a.com/1"]
    storage.files[p.key] = json.dumps({"source": "other", "articles": [good]}).encode()
    assert p.fetch() == []


def test_feed_down_raises_and_keeps_the_pool():
    storage = MemoryStorage()
    down = DownSource()
    p = pooled(down, storage)
    storage.files[p.key] = b"kept"
    with pytest.raises(SourceError):
        p.fetch()
    assert storage.files[p.key] == b"kept"


def test_unreadable_storage_raises_without_overwriting():
    storage = MemoryStorage(fail_read=True)
    with pytest.raises(SourceError, match="could not be read"):
        pooled(FakeSource([article(published_at=at(1))]), storage).fetch()
    assert storage.files == {}


def test_failed_save_raises_naming_the_source():
    storage = MemoryStorage(fail_write=True)
    with pytest.raises(SourceError, match="pool of fake could not be saved"):
        pooled(FakeSource([article(published_at=at(1))]), storage).fetch()


def test_keeps_at_most_the_newest_items():
    storage = MemoryStorage()
    many = [
        article(f"https://a.com/{i}", published_at=NOW - timedelta(seconds=i))
        for i in range(MAX_ITEMS + 5)
    ]
    pooled(FakeSource(many), storage).fetch()
    stored = json.loads(next(iter(storage.files.values())))["articles"]
    assert len(stored) == MAX_ITEMS
    assert stored[0]["url"] == "https://a.com/0"


def test_sources_with_different_names_use_different_entries():
    storage = MemoryStorage()
    a, b = FakeSource([]), FakeSource([])
    a.name, b.name = "A", "B"
    assert pooled(a, storage).key != pooled(b, storage).key


def test_local_storage_accepts_a_folder_with_only_a_pool(tmp_path):
    (tmp_path / "pool").mkdir()
    (tmp_path / "pool" / "x.json").write_text("{}")
    LocalStorage(tmp_path).write("index.html", b"ok")
    assert (tmp_path / "index.html").read_bytes() == b"ok"
