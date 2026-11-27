import hashlib
from dataclasses import dataclass

import polars as pl

from civic_service_requests.manifest import PageRecord
from civic_service_requests.pipelines.land_raw.context import LandRawContext
from civic_service_requests.pipelines.land_raw.read import KEY_COLUMN, FetchedPage


@dataclass(frozen=True)
class PageSummary:
    records: list[PageRecord]
    duplicate_unique_keys: int


def summarise_pages(context: LandRawContext, pages: list[FetchedPage]) -> PageSummary:
    records = [
        PageRecord(
            offset=page.offset,
            path=page.path,
            rows=page.frame.height,
            bytes=len(page.data),
            sha256=hashlib.sha256(page.data).hexdigest(),
        )
        for page in pages
    ]
    keys = [page.frame.get_column(KEY_COLUMN) for page in pages if page.frame.height]
    duplicates = 0
    if keys:
        all_keys = pl.concat(keys)
        duplicates = all_keys.len() - all_keys.n_unique()
    return PageSummary(records=records, duplicate_unique_keys=duplicates)
