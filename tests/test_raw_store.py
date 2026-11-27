from datetime import UTC, date, datetime

from civic_service_requests.manifest import Manifest
from civic_service_requests.raw_store import latest_complete_run, list_complete_runs

WINDOW = (date(2025, 1, 1), date(2025, 1, 8))


def manifest(run_id: str, day: int) -> Manifest:
    return Manifest(
        run_id=run_id,
        source_url="https://fake.example/311.csv",
        window_start=WINDOW[0],
        window_end=WINDOW[1],
        page_size=2,
        retrieved_at=datetime(2025, 2, day, tzinfo=UTC),
        pages=[],
        total_rows=0,
        total_bytes=0,
        source_count=0,
        duplicate_unique_keys=0,
    )


def test_latest_complete_run_is_chosen_by_retrieval_time_and_skips_incomplete_runs(store):
    # Run IDs sort opposite to retrieval time, so listing order alone would pick the wrong one.
    store.write_manifest(manifest("b-older", day=1))
    store.write_manifest(manifest("a-newer", day=2))
    store.write_page("c-incomplete", "page-00000.csv", b"unique_key\n1\n")

    assert [m.run_id for m in list_complete_runs(store)] == ["b-older", "a-newer"]
    latest = latest_complete_run(store, *WINDOW)
    assert latest is not None and latest.run_id == "a-newer"
    assert latest_complete_run(store, date(2025, 3, 1), date(2025, 3, 8)) is None
