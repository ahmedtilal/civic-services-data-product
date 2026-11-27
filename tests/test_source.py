from datetime import date

import httpx
import pytest

from civic_service_requests.source import NycOpenDataSource

WINDOW = (date(2025, 1, 1), date(2025, 1, 8))
WHERE = "created_date >= '2025-01-01T00:00:00' AND created_date < '2025-01-08T00:00:00'"


def source_answering(response: httpx.Response, seen: list[httpx.Request]) -> NycOpenDataSource:
    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return response

    return NycOpenDataSource(client=httpx.Client(transport=httpx.MockTransport(handle)))


def test_fetch_page_asks_for_an_ordered_bounded_page_and_returns_raw_bytes():
    seen: list[httpx.Request] = []
    body = "unique_key\nCafé\n".encode()
    source = source_answering(httpx.Response(200, content=body), seen)

    assert source.fetch_page(*WINDOW, offset=20, limit=10) == body
    assert dict(seen[0].url.params) == {
        "$where": WHERE,
        "$order": "created_date, unique_key",
        "$limit": "10",
        "$offset": "20",
    }


def test_count_reads_the_source_total_for_the_window():
    seen: list[httpx.Request] = []
    source = source_answering(httpx.Response(200, json=[{"count": "42"}]), seen)

    assert source.count(*WINDOW) == 42
    assert seen[0].url.params["$where"] == WHERE


def test_error_responses_raise_instead_of_landing_as_data():
    source = source_answering(httpx.Response(503, content=b"unavailable"), [])

    with pytest.raises(httpx.HTTPStatusError):
        source.fetch_page(*WINDOW, offset=0, limit=10)
