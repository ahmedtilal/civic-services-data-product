# Civic Service Requests

A small, replayable NYC 311 data product built as the project for the **Build a Data Platform on a Budget** series.

This repository starts with the product boundary, a versioned Python package, and its command-line entry point. The pipeline is added in stages: first the GCP foundation, then source profiling, raw landing, refinement, publication, and operations.

## Quick start

Install [uv](https://docs.astral.sh/uv/) 0.13.1 or later in the 0.13 series, then install the project’s Python 3.14 interpreter and locked dependencies:

```sh
uv python install 3.14
make sync
make run
```

The initial CLI exposes:

```sh
uv run --locked civic-data about
uv run --locked civic-data version
```

Use `make check` to run Ruff lint and formatting checks. See [Development](docs/development.md) for the full workflow.

## Project documentation

- [Architecture](docs/architecture.md) — boundaries, layers, and runtime shape.
- [Data product contract](docs/data-product.md) — source, proposed schema, quality rules, and limitations.
- [Development](docs/development.md) — uv, Ruff, and Make commands.
- [Deployment and operations](docs/deployment-and-operations.md) — GCP setup assumptions, identity, cost controls, and run behavior.
- [Series roadmap](docs/roadmap.md) — how each installment extends this checkpoint.
- [Project agent instructions](AGENTS.md) — implementation and documentation rules.

## Project layout

```text
.
├── docs/
├── infra/terraform/
├── src/civic_service_requests/
├── product.yaml
├── Makefile
└── pyproject.toml
```

## Data source

The product uses NYC Open Data’s [311 Service Requests dataset](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9). The first bounded tutorial window is proposed as 1–7 January 2025; the observed row count and captured extract size must be recorded during tutorial preparation.

No cloud project ID, billing account, credentials, or source extract is included in this scaffold.
