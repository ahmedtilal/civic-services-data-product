# Data Product Contract

This is a draft contract for product `civic_service_requests`. The authoritative machine-readable draft is [product.yaml](../product.yaml). Confirm field parsing, null behavior, and proposed names against a captured source extract before publishing a stable table.

## Purpose and consumer

The product supports analysis of NYC service requests over time and by responding agency, problem category, borough, and location. Consumers query the published output (`products.civic_service_requests`); they do not depend on raw files or intermediate tables.

## Source and batch

- **Source:** NYC Open Data, [311 Service Requests from 2020 to Present](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9), dataset `erm2-nwe9`.
- **CSV endpoint:** `https://data.cityofnewyork.us/resource/erm2-nwe9.csv`.
- **Tutorial window:** `created_date >= 2025-01-01T00:00:00` and `created_date < 2025-01-08T00:00:00`. This is a proposed bounded batch, not a measured row-count estimate. Capture and retain the exact extract during tutorial preparation.
- The source is updated daily and may change historical values. A run records the request bounds and retrieval time; the result is the set of responses received, not a transactionally consistent source snapshot.

See NYC's [dataset update notes](https://www.nyc.gov/opendata/news/all-news/311-Service-Requests-Updates) and [column metadata](https://data.cityofnewyork.us/api/views/erm2-nwe9/columns.json).

## Ports and storage

The first implementation is local. Part 6 maps the same layers to Cloud Storage and BigQuery.

- Raw pages are kept byte-for-byte under `data/raw/<run-id>/`.
- `manifest.json` records source URL, date bounds, run ID, retrieval time, page offsets, row counts, sizes, and SHA-256 checksums. Page paths are relative to the raw root. It is written last and marks a complete run.
- Intermediate records remain in the `staging` schema of the local DuckDB file; table names and internal schema are implementation details.
- The consumer output is the view `products.civic_service_requests`. The proposed output fields are below.

## Proposed output schema

| Field | DuckDB type | Source field | Contract |
|---|---|---|---|
| `request_id` | VARCHAR | `unique_key` | Required and unique per service request |
| `created_at` | TIMESTAMP | `created_date` | Required; source has no timezone |
| `closed_at` | TIMESTAMP | `closed_date` | Nullable; source has no timezone |
| `agency_code` | VARCHAR | `agency` | Nullable responding agency acronym |
| `problem_category` | VARCHAR | `complaint_type` | Nullable |
| `problem_detail` | VARCHAR | `descriptor` | Nullable |
| `status` | VARCHAR | `status` | Nullable; new values are observed, not rejected |
| `borough` | VARCHAR | `borough` | Nullable |
| `latitude` | DOUBLE | `latitude` | Nullable |
| `longitude` | DOUBLE | `longitude` | Nullable |

The normalized output names and types are proposals. Verify them against the selected extract before treating this table as stable. The product fields stay the same when the backend changes in part 6.

## Quality expectations

- Reject or quarantine rows without `unique_key` or with an unparseable `created_date`.
- Enforce uniqueness of `request_id`; rerunning the same batch must not duplicate output.
- Allow nullable closing dates and coordinates; report their null rates.
- Treat status and category values as open-ended and surface new values for review.
- Record product ID, run ID, requested bounds, extracted/accepted/rejected counts, duration, and outcome.
- Keep source payloads and credentials out of routine logs.
- Do not set a freshness SLA until source corrections and schedule behavior have been measured.
