"""Where the static site's files go. The site logic is the same for every storage."""

import os
from pathlib import Path
from typing import Protocol, runtime_checkable

from journal.ports import PublishError

# Entries that mark a directory as a journal site (articles.json: layout before
# editions; llm-cache/: AI text cached before the first publish; pool/: feeds
# collected before the first edition).
SITE_MARKERS = ("editions.json", "articles.json", "llm-cache", "pool")


@runtime_checkable
class StoragePort(Protocol):
    """Flat key/value file store; keys are relative POSIX paths like `a/b.html`."""

    def exists(self, key: str) -> bool: ...

    def read(self, key: str) -> bytes | None: ...

    def write(self, key: str, data: bytes) -> None: ...


class LocalStorage:
    """Files under `root`. Each write is atomic (temp file + rename)."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._checked = False

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def read(self, key: str) -> bytes | None:
        try:
            return self._path(key).read_bytes()
        except FileNotFoundError:
            return None

    def write(self, key: str, data: bytes) -> None:
        self._check_root()
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise PublishError(f"refusing to write outside {self.root}: {key!r}")
        return path

    def _check_root(self) -> None:
        """Only missing or empty dirs, or earlier journal sites, may be written to."""
        if self._checked:
            return
        root = self.root
        if root.exists() and not (
            root.is_dir()
            and (
                not any(root.iterdir())
                or any((root / m).exists() for m in SITE_MARKERS)
            )
        ):
            raise PublishError(f"refusing to write to {root}: not a journal site")
        self._checked = True
