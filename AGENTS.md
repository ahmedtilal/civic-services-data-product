# Project Instructions

## Purpose and source of truth

This repository implements the Civic Service Requests data product for the **Build a Data Platform on a Budget** series. Read the workspace [AGENTS.md](../../AGENTS.md) and [NYC 311 product architecture](../../docs/data-products/nyc-311-civic-services-v1.md) before changing architecture or data contracts.

Use the full product ID `civic_service_requests`. The first source is the NYC Open Data 311 dataset `erm2-nwe9`. This is one domain product and a learning project; do not claim that it demonstrates independent mesh teams or organization-wide data mesh governance.

## Architecture constraints

- Keep the installable package under `src/civic_service_requests/`; keep the Typer CLI thin.
- Use Pydantic at command and pipeline boundaries. Masoora wires in-process pipeline steps; it is not durable storage, a scheduler, or a persistent catalog.
- Preserve source responses unchanged in Cloud Storage with a run manifest. Only manifest-complete runs are inputs to downstream stages.
- Keep intermediate BigQuery data in `civic_services_staging`; expose the consumer contract through `civic_services_products`.
- Keep Cloud Storage and BigQuery co-located in `europe-west2` for the tutorial deployment.
- Make writes safe to retry. The live NYC source can change older rows, so never imply that created-date filtering alone gives a freshness guarantee.
- Do not publish a freshness SLA until source changes and schedule behavior have been measured.
- Keep raw paths and internal staging tables out of the consumer contract.

## Python workflow

- Use Python 3.14 for the current supported runtime and respect the range in `pyproject.toml`.
- Manage dependencies and the environment with uv. Pin direct dependencies in `pyproject.toml`, update `uv.lock`, and use `uv sync --locked` for normal installs.
- Keep Ruff configuration in `pyproject.toml`; use `make check` for lint and formatting checks.
- Put runtime code in the source package. Keep cloud access behind small interfaces so local command help and pure transformations do not need credentials.
- Add meaningful checks for parsing, row quality, idempotency, and manifest handling when those features are implemented.

## Security and operations

- Use Application Default Credentials locally and the attached service account on Cloud Run. Never add service-account key files, tokens, or real project identifiers.
- Do not log source row payloads or credentials. Log run identifiers, requested bounds, counts, duration, and outcome.
- Keep Terraform state, local `.tfvars`, build output, virtual environments, and caches out of Git.
- Review `terraform plan` before applying infrastructure. A budget alert is a warning, not a spending cap.

## Documentation

- Keep `product.yaml`, [the data product contract](docs/data-product.md), and [the architecture](docs/architecture.md) aligned.
- Label proposed values and cost estimates. Do not invent a source row count, measured cost, contact, or operational result.
- Link technical claims to primary NYC Open Data, Google Cloud, Python, or package documentation.
- Keep the series roadmap aligned with the workspace product architecture.
