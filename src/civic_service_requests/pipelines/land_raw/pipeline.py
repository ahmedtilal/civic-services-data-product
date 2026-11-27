import logging
import time

from masoora import Pipeline, PipelineBuilder, StepExecutionError

from civic_service_requests.manifest import Manifest
from civic_service_requests.pipelines.land_raw.context import LandRawContext
from civic_service_requests.pipelines.land_raw.read import (
    make_fetch_pages,
    make_observe_source_count,
)
from civic_service_requests.pipelines.land_raw.transform import summarise_pages
from civic_service_requests.pipelines.land_raw.write import make_write_manifest
from civic_service_requests.raw_store import RawStore
from civic_service_requests.source import RawSource

PAGES = "pages"
SOURCE_COUNT = "source_count"
SUMMARY = "summary"

logger = logging.getLogger(__name__)


def build_pipeline(source: RawSource, store: RawStore) -> Pipeline[LandRawContext]:
    return (
        PipelineBuilder[LandRawContext]()
        .with_read_step(make_fetch_pages(source, store), output=PAGES)
        .with_read_step(make_observe_source_count(source), output=SOURCE_COUNT)
        .with_transform_step(summarise_pages, inputs=[PAGES], output=SUMMARY)
        .with_write_step(
            make_write_manifest(source.source_url, store), inputs=[SUMMARY, SOURCE_COUNT]
        )
        .build()
    )


def run(context: LandRawContext, source: RawSource, store: RawStore) -> Manifest:
    """Run one batch and log run facts, never row payloads.

    Raises StepExecutionError if the run stops; the run is then left incomplete.
    """
    bounds = f"{context.window_start}..{context.window_end}"
    logger.info("run_id=%s bounds=%s started", context.run_id, bounds)
    began = time.monotonic()
    try:
        build_pipeline(source, store).run(context)
    except StepExecutionError:
        logger.error(
            "run_id=%s bounds=%s outcome=incomplete duration=%.1fs",
            context.run_id,
            bounds,
            time.monotonic() - began,
        )
        raise
    manifest = store.read_manifest(context.run_id)
    if manifest is None:
        raise RuntimeError(f"run {context.run_id} finished without a manifest")
    logger.info(
        "run_id=%s bounds=%s outcome=complete pages=%d rows=%d duplicates=%d duration=%.1fs",
        context.run_id,
        bounds,
        len(manifest.pages),
        manifest.total_rows,
        manifest.duplicate_unique_keys,
        time.monotonic() - began,
    )
    return manifest
