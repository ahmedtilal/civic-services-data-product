import secrets
from datetime import UTC, date, datetime

from masoora import PipelineContext
from pydantic import Field, model_validator

DEFAULT_WINDOW_START = date(2025, 1, 1)
DEFAULT_WINDOW_END = date(2025, 1, 8)
DEFAULT_PAGE_SIZE = 10_000
DEFAULT_RETRIES = 0
RUN_ID_PATTERN = r"^\d{8}T\d{6}Z-[0-9a-f]{6}$"


def new_run_id() -> str:
    """UTC timestamp plus a random suffix, so run IDs sort by time."""
    return f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{secrets.token_hex(3)}"


class LandRawContext(PipelineContext):
    window_start: date = DEFAULT_WINDOW_START
    window_end: date = Field(default=DEFAULT_WINDOW_END, description="Exclusive end of the batch.")
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, gt=0)
    retries: int = Field(default=DEFAULT_RETRIES, ge=0, le=10, description="Retries per page.")
    retry_delay_seconds: float = Field(default=1.0, ge=0)
    run_id: str = Field(default_factory=new_run_id, pattern=RUN_ID_PATTERN)
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Recorded in the manifest as the run's retrieval time.",
    )

    @model_validator(mode="after")
    def _window_is_ordered(self) -> LandRawContext:
        if self.window_end <= self.window_start:
            raise ValueError("window_end must be after window_start")
        return self
