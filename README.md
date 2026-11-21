# Civic Service Requests

A small, replayable NYC 311 data product built as the project for the **Build a Data Platform on a Budget** series.

The project is local first. It starts with the product boundary, a versioned Python package, and its command-line entry point, then adds the pipeline in stages: source profiling, raw landing, refinement, a local output port, a Google Cloud deployment, and operations.

## Branches

Each part of the series is a branch. A branch is the previous branch plus one commit, so the diff between neighbouring branches is the change its article describes. See the [series roadmap](docs/roadmap.md) for the full list.

You are on `part-01-design-and-requirements`, which covers articles 1 and 2.

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
- [Series roadmap](docs/roadmap.md) — the branch for each installment.
- [Project agent instructions](AGENTS.md) — implementation and documentation rules.

## Project layout

```text
.
├── docs/
├── src/civic_service_requests/
├── product.yaml
├── Makefile
└── pyproject.toml
```

## Data source

The product uses NYC Open Data’s [311 Service Requests dataset](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9). The first bounded tutorial window is proposed as 1–7 January 2025; the observed row count and captured extract size are recorded in part 2.

No cloud project ID, billing account, credentials, or source extract is included in this branch.
