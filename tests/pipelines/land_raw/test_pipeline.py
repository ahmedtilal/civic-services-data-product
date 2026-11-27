from pathlib import Path

import httpx
import pytest
from masoora import StepExecutionError

from civic_service_requests.pipelines.land_raw import LandRawContext, build_pipeline, run
from civic_service_requests.pipelines.land_raw.pipeline import (
    PAGES,
    SOURCE_COUNT,
    SUMMARY,
)
from civic_service_requests.pipelines.land_raw.read import FetchedPage, parse_page
from civic_service_requests.raw_store import LocalRawStore
from civic_service_requests.source import NycOpenDataSource

PAGE = b"unique_key\n1\n"
FETCHED = [FetchedPage(offset=0, path="run/0.csv", data=PAGE, frame=parse_page(PAGE))]


def _refuse(request: httpx.Request) -> httpx.Response:
    raise AssertionError("the wiring tests must not call the source")


# make_pipeline_fixture has no scope option, so this runs the testable pipeline itself, once.
@pytest.fixture(scope="module")
def wired():
    pipeline = build_pipeline(
        NycOpenDataSource(client=httpx.Client(transport=httpx.MockTransport(_refuse))),
        LocalRawStore(Path("never-written")),
    )
    testable = pipeline.to_testable(reads={PAGES: FETCHED, SOURCE_COUNT: 7})
    return testable.run(LandRawContext())


def test_summary_is_built_from_the_fetched_pages(wired):
    assert [record.path for record in wired.catalog[SUMMARY].records] == ["run/0.csv"]


def test_manifest_write_receives_the_summary_and_source_count(wired):
    assert wired.written == {SUMMARY: wired.catalog[SUMMARY], SOURCE_COUNT: 7}


def test_complete_run_keeps_pages_byte_for_byte_and_records_them(
    make_source, make_context, store: LocalRawStore
):
    source = make_source([1, 2, 3])
    context = make_context()

    manifest = run(context, source, store)

    assert manifest == store.read_manifest(context.run_id)
    assert [store.read_page(p.path) for p in manifest.pages] == [source.served[0], source.served[2]]
    assert (manifest.total_rows, manifest.source_count) == (3, 3)


def test_stopped_run_keeps_its_pages_and_has_no_manifest(make_source, make_context, store):
    context = make_context()

    with pytest.raises(StepExecutionError):
        build_pipeline(make_source([1, 2, 3], fail_pages={1: 1}), store).run(context)

    assert store.read_manifest(context.run_id) is None
    assert store.read_page(f"{context.run_id}/page-00000.csv")


def test_rerun_of_a_batch_never_overwrites_the_earlier_run(make_source, make_context, store):
    first = run(make_context(), make_source([1]), store)
    second = run(make_context(), make_source([1, 2]), store)

    assert first.run_id != second.run_id
    assert store.read_manifest(first.run_id) == first


def test_logs_carry_run_facts_but_no_row_payloads(make_source, make_context, store, caplog):
    caplog.set_level("INFO")
    context = make_context()

    run(context, make_source([1]), store)

    assert context.run_id in caplog.text
    assert "2025-01-01" in caplog.text
    assert "Café" not in caplog.text
