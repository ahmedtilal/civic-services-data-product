# Development

## Supported toolchain

This scaffold uses Python 3.14, uv 0.13.1 or later in the 0.13 series, and Ruff 0.17.1. These are the versions checked for the initial scaffold on 18 October 2026. Python 3.15 is now stable, but the dependencies this series adds (Masoora and the Google Cloud clients) list support through Python 3.14; use 3.14 until they declare and verify 3.15 support.

The exact direct dependency versions are recorded in `pyproject.toml` and `uv.lock`. Ruff configuration also lives in `pyproject.toml`.

## Set up

Install uv using the [official Astral instructions](https://docs.astral.sh/uv/getting-started/installation/), then install Python and the locked environment:

```sh
uv python install 3.14
make sync
```

No cloud account or credentials are needed until part 6, which adds the Google Cloud setup.

## Make targets

| Command | Purpose |
|---|---|
| `make help` | List the available targets |
| `make sync` | Install the locked project and development dependencies |
| `make run` | Show the CLI help |
| `make lint` | Run Ruff lint checks |
| `make format` | Format Python files with Ruff |
| `make format-check` | Check formatting without changing files |
| `make check` | Run lint and formatting checks |
| `make clean` | Remove local environments, caches, and build output |

The initial `check` target does not run a test suite. Add focused tests alongside parsing, quality, idempotency, and manifest behavior as those features are implemented.

## Dependencies

Add or remove direct dependencies with uv and exact versions, then commit both `pyproject.toml` and the updated `uv.lock`. Use `uv sync --locked` for normal setup so dependency drift is reported instead of silently changing the environment.

```sh
uv add "package==x.y.z"
uv add --dev "tool==x.y.z"
uv lock
```

Update uv and Ruff only after checking their current release notes and compatibility. The project requires uv 0.13.1 or later in the 0.13 series; update `tool.uv.required-version` together with the lockfile when adopting another series.
