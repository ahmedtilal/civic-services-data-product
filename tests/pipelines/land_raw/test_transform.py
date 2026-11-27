import hashlib

from civic_service_requests.pipelines.land_raw.read import FetchedPage, parse_page
from civic_service_requests.pipelines.land_raw.transform import summarise_pages


def page(offset: int, data: bytes) -> FetchedPage:
    return FetchedPage(offset=offset, path=f"run/{offset}.csv", data=data, frame=parse_page(data))


def test_pages_are_summarised_with_checksums_and_surplus_duplicate_keys(make_context):
    first = b"unique_key\n1\n2\n2\n"
    second = b"unique_key\n2\n3\n"
    header_only = b"unique_key\n"

    summary = summarise_pages(
        make_context(), [page(0, first), page(3, second), page(6, header_only)]
    )

    assert [record.rows for record in summary.records] == [3, 2, 0]
    assert summary.records[0].bytes == len(first)
    assert summary.records[0].sha256 == hashlib.sha256(first).hexdigest()
    assert summary.duplicate_unique_keys == 2
