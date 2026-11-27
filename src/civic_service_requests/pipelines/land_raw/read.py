import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

import polars as pl

from civic_service_requests.pipelines.land_raw.context import LandRawContext
from civic_service_requests.raw_store import RawStore
from civic_service_requests.source import RawSource

KEY_COLUMN = "unique_key"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchedPage:
    offset: int
    path: str
    data: bytes
    frame: pl.DataFrame


def parse_page(data: bytes) -> pl.DataFrame:
    frame = pl.read_csv(data, infer_schema=False, raise_if_empty=False)
    if frame.height and KEY_COLUMN not in frame.columns:
        raise ValueError(f"page has no {KEY_COLUMN!r} column")
    return frame


def _fetch_with_retries(source: RawSource, context: LandRawContext, offset: int) -> bytes:
    attempts = context.retries + 1
    for attempt in range(1, attempts + 1):
        try:
            return source.fetch_page(
                context.window_start, context.window_end, offset, context.page_size
            )
        except Exception as exc:
            logger.warning(
                "run_id=%s offset=%d attempt=%d/%d failed: %s",
                context.run_id,
                offset,
                attempt,
                attempts,
                type(exc).__name__,
            )
            if attempt == attempts:
                raise
            time.sleep(context.retry_delay_seconds)
    raise AssertionError("unreachable")


def make_fetch_pages(
    source: RawSource, store: RawStore
) -> Callable[[LandRawContext], list[FetchedPage]]:
    def fetch_pages(context: LandRawContext) -> list[FetchedPage]:
        pages: list[FetchedPage] = []
        offset = 0
        while True:
            data = _fetch_with_retries(source, context, offset)
            path = store.write_page(context.run_id, f"page-{len(pages):05d}.csv", data)
            frame = parse_page(data)
            pages.append(FetchedPage(offset=offset, path=path, data=data, frame=frame))
            if frame.height < context.page_size:
                return pages
            offset += context.page_size

    return fetch_pages


def make_observe_source_count(source: RawSource) -> Callable[[LandRawContext], int | None]:
    def observe_source_count(context: LandRawContext) -> int | None:
        try:
            return source.count(context.window_start, context.window_end)
        except Exception as exc:
            logger.warning(
                "run_id=%s source count unavailable: %s", context.run_id, type(exc).__name__
            )
            return None

    return observe_source_count
