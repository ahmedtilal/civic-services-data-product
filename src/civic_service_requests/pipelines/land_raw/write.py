from collections.abc import Callable

from civic_service_requests.manifest import Manifest
from civic_service_requests.pipelines.land_raw.context import LandRawContext
from civic_service_requests.pipelines.land_raw.transform import PageSummary
from civic_service_requests.raw_store import RawStore


def make_write_manifest(
    source_url: str, store: RawStore
) -> Callable[[LandRawContext, PageSummary, int | None], None]:
    def write_manifest(
        context: LandRawContext, summary: PageSummary, source_count: int | None
    ) -> None:
        store.write_manifest(
            Manifest(
                run_id=context.run_id,
                source_url=source_url,
                window_start=context.window_start,
                window_end=context.window_end,
                page_size=context.page_size,
                retrieved_at=context.started_at,
                pages=summary.records,
                total_rows=sum(record.rows for record in summary.records),
                total_bytes=sum(record.bytes for record in summary.records),
                source_count=source_count,
                duplicate_unique_keys=summary.duplicate_unique_keys,
            )
        )

    return write_manifest
