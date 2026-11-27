from datetime import date
from typing import Protocol

import httpx

CSV_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
JSON_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
ORDER = "created_date, unique_key"


class RawSource(Protocol):
    source_url: str

    def count(self, start: date, end: date) -> int:
        """The source's own row count for the window (end exclusive)."""
        ...

    def fetch_page(self, start: date, end: date, offset: int, limit: int) -> bytes:
        """One CSV page, ordered by `created_date, unique_key`, as raw bytes."""
        ...


def where_clause(start: date, end: date) -> str:
    return f"created_date >= '{start}T00:00:00' AND created_date < '{end}T00:00:00'"


class NycOpenDataSource:
    source_url = CSV_URL

    def __init__(self, client: httpx.Client | None = None, timeout: float = 60.0) -> None:
        self._client = client or httpx.Client(timeout=timeout)

    def count(self, start: date, end: date) -> int:
        response = self._client.get(
            JSON_URL, params={"$select": "count(*)", "$where": where_clause(start, end)}
        )
        response.raise_for_status()
        return int(response.json()[0]["count"])

    def fetch_page(self, start: date, end: date, offset: int, limit: int) -> bytes:
        response = self._client.get(
            CSV_URL,
            params={
                "$where": where_clause(start, end),
                "$order": ORDER,
                "$limit": limit,
                "$offset": offset,
            },
        )
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        self._client.close()
