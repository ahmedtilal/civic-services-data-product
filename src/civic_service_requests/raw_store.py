import os
from datetime import date
from pathlib import Path
from typing import Protocol

from civic_service_requests.manifest import MANIFEST_NAME, Manifest

DEFAULT_RAW_DIR = Path("data/raw")


class RawStore(Protocol):
    """Paths are relative to the store root, so the root can move without rewriting manifests."""

    def write_page(self, run_id: str, name: str, data: bytes) -> str:
        """Store one page and return its path relative to the raw root."""
        ...

    def write_manifest(self, manifest: Manifest) -> None:
        """The manifest must only become visible once fully written."""
        ...

    def read_page(self, path: str) -> bytes: ...

    def read_manifest(self, run_id: str) -> Manifest | None:
        """None means the run is incomplete."""
        ...

    def list_runs(self) -> list[str]:
        """Every run ID with any files, complete or not, sorted."""
        ...


class LocalRawStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_page(self, run_id: str, name: str, data: bytes) -> str:
        relative = f"{run_id}/{name}"
        self._write_atomic(self.root / relative, data)
        return relative

    def write_manifest(self, manifest: Manifest) -> None:
        payload = manifest.model_dump_json(indent=2).encode()
        self._write_atomic(self.root / manifest.run_id / MANIFEST_NAME, payload)

    def read_page(self, path: str) -> bytes:
        return (self.root / path).read_bytes()

    def read_manifest(self, run_id: str) -> Manifest | None:
        path = self.root / run_id / MANIFEST_NAME
        if not path.exists():
            return None
        return Manifest.model_validate_json(path.read_bytes())

    def list_runs(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(path.name for path in self.root.iterdir() if path.is_dir())

    @staticmethod
    def _write_atomic(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_bytes(data)
        os.replace(temp, path)


def list_complete_runs(store: RawStore) -> list[Manifest]:
    """Oldest retrieval first."""
    manifests = [
        manifest
        for run_id in store.list_runs()
        if (manifest := store.read_manifest(run_id)) is not None
    ]
    return sorted(manifests, key=lambda manifest: (manifest.retrieved_at, manifest.run_id))


def latest_complete_run(store: RawStore, window_start: date, window_end: date) -> Manifest | None:
    matches = [
        manifest
        for manifest in list_complete_runs(store)
        if (manifest.window_start, manifest.window_end) == (window_start, window_end)
    ]
    return matches[-1] if matches else None
