from collections.abc import Callable
from datetime import date
from typing import Any

import pytest

from civic_service_requests.pipelines.land_raw import LandRawContext
from civic_service_requests.raw_store import LocalRawStore

HEADER = "unique_key,created_date,descriptor"


class FakeSource:
    source_url = "https://fake.example/311.csv"

    def __init__(
        self, keys: list[int], fail_pages: dict[int, int] | None = None, count_fails: bool = False
    ) -> None:
        # A quoted newline and non-ASCII text check that bytes are kept as received.
        self.rows = [f'{key},2025-01-02T00:00:00,"Noise,\nCafé {key}"' for key in keys]
        self.fail_pages = dict(fail_pages or {})  # page index -> failures still to raise
        self.count_fails = count_fails
        self.requests: list[int] = []
        self.served: dict[int, bytes] = {}

    def count(self, start: date, end: date) -> int:
        if self.count_fails:
            raise ConnectionError("boom")
        return len(self.rows)

    def fetch_page(self, start: date, end: date, offset: int, limit: int) -> bytes:
        self.requests.append(offset)
        index = offset // limit
        if self.fail_pages.get(index, 0) > 0:
            self.fail_pages[index] -= 1
            raise ConnectionError("boom")
        data = ("\n".join([HEADER, *self.rows[offset : offset + limit]]) + "\n").encode()
        self.served[offset] = data
        return data

    def close(self) -> None:
        pass


@pytest.fixture
def make_source() -> type[FakeSource]:
    return FakeSource


@pytest.fixture
def make_context() -> Callable[..., LandRawContext]:
    def make(**overrides: Any) -> LandRawContext:
        options: dict[str, Any] = {"page_size": 2, "retry_delay_seconds": 0, **overrides}
        return LandRawContext(**options)

    return make


@pytest.fixture
def store(tmp_path) -> LocalRawStore:
    return LocalRawStore(tmp_path / "raw")
