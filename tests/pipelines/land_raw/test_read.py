import pytest

from civic_service_requests.pipelines.land_raw.read import (
    make_fetch_pages,
    make_observe_source_count,
)


@pytest.mark.parametrize(
    ("keys", "page_rows"),
    [([1, 2, 3], [2, 1]), ([1, 2, 3, 4], [2, 2, 0])],
)
def test_paging_stops_after_the_first_short_page(make_source, make_context, store, keys, page_rows):
    pages = make_fetch_pages(make_source(keys), store)(make_context())

    assert [page.frame.height for page in pages] == page_rows


def test_transient_failures_within_the_retry_limit_are_retried(make_source, make_context, store):
    source = make_source([1, 2, 3], fail_pages={1: 2})

    pages = make_fetch_pages(source, store)(make_context(retries=2))

    assert sum(page.frame.height for page in pages) == 3


def test_retries_are_bounded(make_source, make_context, store):
    source = make_source([1, 2, 3], fail_pages={1: 3})

    with pytest.raises(ConnectionError):
        make_fetch_pages(source, store)(make_context(retries=2))

    assert source.requests.count(2) == 3


def test_unparseable_page_is_stored_before_it_is_rejected(make_source, make_context, store):
    source = make_source([1])
    source.fetch_page = lambda start, end, offset, limit: b"id\n1\n"
    context = make_context()

    with pytest.raises(ValueError, match="unique_key"):
        make_fetch_pages(source, store)(context)

    assert store.read_page(f"{context.run_id}/page-00000.csv") == b"id\n1\n"


def test_unavailable_source_count_is_recorded_as_none(make_source, make_context):
    observe = make_observe_source_count(make_source([1], count_fails=True))

    assert observe(make_context()) is None
