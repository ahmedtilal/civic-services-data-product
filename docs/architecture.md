# Architecture

## Product scope

Civic Service Requests is one domain data product in a learning project. It publishes documented NYC 311 data for analysis by request date, agency, problem category, borough, and location.

The project demonstrates product boundaries, contracts, and quality expectations on a single source. It does not claim to model independent teams or prove organizational data mesh governance.

## Data flow

```mermaid
flowchart LR
  SRC[NYC Open Data 311 CSV] --> RAW[Input port: unchanged raw files and manifest]
  RAW --> VALIDATE[Validate and normalize]
  VALIDATE --> INT[Intermediate staging schema]
  INT --> OUT[Published output port]
  OUT --> USER[Analyst or another product]
```

- **Input port:** a bounded CSV extract from NYC Open Data. Later work can add other source formats.
- **Raw layer:** unchanged CSV pages and a manifest. The manifest records the source, requested window, retrieval time, counts, sizes, and checksums. It marks the run complete only after all pages are written.
- **Intermediate layer:** validated and normalized records in a private `staging` schema. Its table layout can change as the pipeline learns more about the source.
- **Output port:** the documented contract in the `products` schema. Consumers depend on this interface rather than raw files or staging tables.

The draft schema and quality expectations live in [the data product contract](data-product.md) and machine-readable [product.yaml](../product.yaml).

## Local first

The first version runs on a laptop: raw pages are files on disk, and the intermediate table and output view live in one DuckDB file. A cloud account is not required until [part 6](roadmap.md).

Cloud access sits behind small interfaces, such as a raw store with read and write operations for pages and manifests. Part 6 adds Cloud Storage and BigQuery implementations without changing the pipeline steps or the product fields. Pure transformations and `--help` never need credentials.

Planned cloud shape, to be confirmed in part 6: one project, with Cloud Storage and BigQuery co-located in `europe-west2`, a staging dataset `civic_services_staging`, and a consumer dataset `civic_services_products`.

## Runtime

One installable Python package exposes the `civic-data` Typer CLI. Command options are validated at the boundary with Pydantic. Masoora wires the internal steps in process; it is not durable storage, a scheduler, or a persistent catalog.

The planned pipeline commands are:

1. `land-raw` fetches the bounded source batch and writes original pages plus a manifest.
2. `build-intermediate` reads a completed raw run, validates and normalizes it, and merges staging data.
3. `publish-product` checks quality and replaces the consumer-facing output.
4. `run-daily` calls the required stages in sequence for the first scheduled job (part 7).

## Reliability boundaries

- Each run receives a unique run ID and preserves its source input for replay.
- Downstream stages read only runs that have a completion manifest.
- Writes must be safe to retry; a rerun of the same batch must not duplicate output.
- The NYC source may revise older records. A created-date window is a bounded batch, not a complete incremental-change strategy.
- No freshness SLA is published until update behavior and scheduled runs have been measured.
