from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

MANIFEST_NAME = "manifest.json"


class PageRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    offset: int = Field(ge=0)
    path: str = Field(description="Relative to the raw root.")
    rows: int = Field(ge=0)
    bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class Manifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    source_url: str
    window_start: date
    window_end: date = Field(description="Exclusive end of the batch.")
    page_size: int
    retrieved_at: datetime
    pages: list[PageRecord]
    total_rows: int
    total_bytes: int
    source_count: int | None = Field(
        description="The source's own count at the time of the run; observed, never enforced."
    )
    duplicate_unique_keys: int = Field(description="Surplus unique_key occurrences across pages.")
