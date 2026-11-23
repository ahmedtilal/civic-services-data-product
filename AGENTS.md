# Project Instructions

## Purpose and source of truth

This repository implements the Civic Service Requests data product for the **Build a Data Platform on a Budget** series. Read the workspace [AGENTS.md](../../AGENTS.md) and [NYC 311 product architecture](../../docs/data-products/nyc-311-civic-services-v1.md) before changing architecture or data contracts.

Use the full product ID `civic_service_requests`. The first source is the NYC Open Data 311 dataset `erm2-nwe9`. This is one domain product and a learning project; do not claim that it demonstrates independent mesh teams or organization-wide data mesh governance.

## Branches and this file

Each part of the series is a branch, and a branch is the previous one plus one squashed commit. See [the roadmap](docs/roadmap.md) for the list. This file describes the branch it is on: update it in the same commit that changes what the branch contains, and do not describe code or infrastructure that a later branch adds.

**Current branch: `part-02-explore-source` (article 3).** It adds a marimo exploration notebook, `notebooks/nyc_311_exploration.py`, and records measured source volume in the contract docs. There is no pipeline code, no tests, and no cloud resources yet.

- The notebook declares its own dependencies with inline script metadata, pinned, so `pyproject.toml` stays unchanged until a part's runtime code needs a package. It reads from the source only and writes nothing.
- Record measured source numbers with the date and a note that they are point-in-time. Never record an estimate as a measurement.

Later parts add these rules to this file as the matching code lands:

- **Part 3** (`part-03-land-raw-locally`): Masoora pipelines, Pydantic run contexts, the raw-store interface, and the raw landing and manifest rules.
- **Part 4**: the intermediate layer and the `staging` DuckDB schema.
- **Part 5**: the quality gate and the `products` output view.
- **Part 6**: Google Cloud, Terraform, `europe-west2`, and credential rules.
- **Part 7**: scheduling, logging fields, and alerts.

## Architecture constraints

- Keep the installable package under `src/civic_service_requests/`; keep the Typer CLI thin.
- Use Pydantic at command and pipeline boundaries.
- The project is local first. Do not add cloud dependencies, credentials, or infrastructure before part 6.
- Keep consumer-facing output separate from raw files and internal staging data.
- Make writes safe to retry. The live NYC source can change older rows, so never imply that created-date filtering alone gives a freshness guarantee.
- Do not publish a freshness SLA until source changes and schedule behavior have been measured.

## Python workflow

- Use Python 3.14 for the current supported runtime and respect the range in `pyproject.toml`.
- Manage dependencies and the environment with uv. Pin direct dependencies in `pyproject.toml`, update `uv.lock`, and use `uv sync --locked` for normal installs. Add a dependency only in the part that first uses it.
- Keep Ruff configuration in `pyproject.toml`; use `make check` for lint and formatting checks.
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
