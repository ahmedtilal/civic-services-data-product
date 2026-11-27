# Project Instructions

## Purpose and source of truth

This repository implements the Civic Service Requests data product for the **Build a Data Platform on a Budget** series. Read the workspace [AGENTS.md](../../AGENTS.md) and [NYC 311 product architecture](../../docs/data-products/nyc-311-civic-services-v1.md) before changing architecture or data contracts.

Use the full product ID `civic_service_requests`. The first source is the NYC Open Data 311 dataset `erm2-nwe9`. This is one domain product and a learning project; do not claim that it demonstrates independent mesh teams or organization-wide data mesh governance.

## Branches and this file

Each part of the series is a branch, and a branch is the previous one plus one squashed commit. See [the roadmap](docs/roadmap.md) for the list. This file describes the branch it is on: update it in the same commit that changes what the branch contains, and do not describe code or infrastructure that a later branch adds.

**Current branch: `part-03-land-raw-locally` (article 4).** It adds `civic-data land-raw`, a Masoora pipeline that lands one batch as byte-for-byte CSV pages plus a manifest in a local raw store, with pytest tests and [ADR 0001](docs/adr/0001-run-completeness-and-reconciliation.md). There is no intermediate layer, no DuckDB, and no cloud resources yet.

- The exploration notebook (`notebooks/nyc_311_exploration.py`) still declares its own pinned dependencies and writes nothing.
- Record measured source numbers with the date and a note that they are point-in-time. Never record an estimate as a measurement. Tests must not depend on live source numbers.

### Masoora and run contexts

- Masoora wires steps in process only. It is not storage, a scheduler, or a catalog.
- Each pipeline has a Pydantic `PipelineContext` subclass that validates options (window bounds, page size, retries) before any request. The Typer CLI only builds the context, calls the pipeline's `run`, and unwraps `StepExecutionError` into a clear message and exit code.
- Build pipelines with a factory that takes the source and store (`build_pipeline(source, store)`), so tests inject fakes.

### Raw store, landing, and manifest rules

- Storage sits behind the `RawStore` interface; `LocalRawStore` writes `data/raw/<run-id>/`. Manifest page paths are relative to the raw root. Do not add cloud code before part 6.
- Keep pages byte-for-byte as received. Never rewrite, reformat, or delete a page.
- Write the manifest last and atomically. Its presence is the only thing that makes a run complete; incomplete runs are kept and ignored, never cleaned up or resumed.
- Reruns create a new run ID and new files; never overwrite an earlier run. Downstream reads the latest complete run for a batch.
- Retries default to 0. The source count is recorded, not enforced. Paging is not locked, so skipped rows are possible; only repeated `unique_key` values are counted.
- Tests need no network. Their layout and scope are in [the coding standards](CODING_STANDARDS.md#tests).
- Logs carry run ID, bounds, counts, duration, and outcome only.

Later parts add these rules to this file as the matching code lands:

- **Part 4**: the intermediate layer and the `staging` DuckDB schema.
- **Part 5**: the quality gate and the `products` output view.
- **Part 6**: Google Cloud, Terraform, `europe-west2`, and credential rules.
- **Part 7**: scheduling, logging fields, and alerts.

## Architecture constraints

- Keep the installable package under `src/civic_service_requests/`; keep the Typer CLI thin.
- Each pipeline is a package, `pipelines/<name>/`: `context.py`, `read.py`, `transform.py`, `write.py` for its steps, and `pipeline.py` with `build_pipeline` and `run`. Add `transform.py` only when there is a transform. Code shared by pipelines (manifest, raw store, source) sits at the package root. Other code imports a pipeline through its `__init__.py`; the CLI may also import its default constants from `context.py`.
- Read [the coding standards](CODING_STANDARDS.md) before writing or reviewing Python or tests.
- Use Pydantic at command and pipeline boundaries.
- The project is local first. Do not add cloud dependencies, credentials, or infrastructure before part 6.
- Keep consumer-facing output separate from raw files and internal staging data.
- Make writes safe to retry. The live NYC source can change older rows, so never imply that created-date filtering alone gives a freshness guarantee.
- Do not publish a freshness SLA until source changes and schedule behavior have been measured.

## Python workflow

- Use Python 3.14 for the current supported runtime and respect the range in `pyproject.toml`.
- Manage dependencies and the environment with uv. Pin direct dependencies in `pyproject.toml`, update `uv.lock`, and use `uv sync --locked` for normal installs. Add a dependency only in the part that first uses it.
- Keep Ruff configuration in `pyproject.toml`; run `make check` (lint, format, Pyrefly types, tests) before every commit; CI runs the same target on every pull request.
- Put runtime code in the source package. Keep storage behind small interfaces so command help and pure transformations do not need credentials.
- Add meaningful checks for parsing, row quality, idempotency, and manifest handling when those features are implemented.

## Security and operations

- Never add service-account key files, tokens, or real project identifiers.
- Do not log source row payloads or credentials. Log run identifiers, requested bounds, counts, duration, and outcome.
- Keep local data, `.env` files, build output, virtual environments, and caches out of Git. `.scratch/` and `.claude/` are ignored.

## Documentation

- Keep `product.yaml`, [the data product contract](docs/data-product.md), and [the architecture](docs/architecture.md) aligned.
- Label proposed values and cost estimates. Do not invent a source row count, measured cost, contact, or operational result.
- Link technical claims to primary NYC Open Data, Python, package, or (from part 6) Google Cloud documentation. Masoora documentation is at <https://ahmedtilal.github.io/masoora/>.
- Keep the series roadmap aligned with the workspace product architecture and with the articles in `/Users/ahmed/workspace/atosman/content/articles`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues, with one milestone per part of the series. See `docs/agents/issue-tracker.md`. `.scratch/` is for local notes only and is gitignored.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo; read the root `GLOSSARY.md` and relevant ADRs in `docs/adr/`. See `docs/agents/domain.md`.
