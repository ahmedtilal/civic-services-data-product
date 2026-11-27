# Development

## Supported toolchain

This scaffold uses Python 3.14, uv 0.13.1 or later in the 0.13 series, and Ruff 0.17.1. These are the versions checked for the initial scaffold on 18 October 2026. Python 3.15 is now stable, but the dependencies this series adds (Masoora and the Google Cloud clients) list support through Python 3.14; use 3.14 until they declare and verify 3.15 support.

The exact direct dependency versions are recorded in `pyproject.toml` and `uv.lock`. Ruff configuration also lives in `pyproject.toml`.

## Set up

Install uv using the [official Astral instructions](https://docs.astral.sh/uv/getting-started/installation/), then install Python and the locked environment:

```sh
uv python install 3.14
make sync
make hooks
```

No cloud account or credentials are needed until part 6, which adds the Google Cloud setup.

## Notebook

The source exploration notebook is a marimo app stored as a Python file. It lists its own pinned dependencies in inline script metadata, so it does not need the project environment:

```sh
uvx marimo edit --sandbox notebooks/nyc_311_exploration.py
```

To check that every cell runs without opening an editor, run `uv run --script notebooks/nyc_311_exploration.py`. It reads from the NYC Open Data API and writes nothing. The final cell downloads the whole window only if you switch it on.

## Make targets

| Command | Purpose |
|---|---|
| `make help` | List the available targets |
| `make sync` | Install the locked project and development dependencies |
| `make run` | Show the CLI help |
| `make lint` | Run Ruff lint checks |
| `make format` | Format Python files with Ruff |
| `make format-check` | Check formatting without changing files |
| `make test` | Run the pytest suite |
| `make typecheck` | Run Pyrefly type checks |
| `make check` | Run lint, formatting checks, type checks, and tests |
| `make hooks` | Enable the Git pre-push hook |
| `make clean` | Remove local environments, caches, and build output |

Tests use an in-process fake of the NYC CSV endpoint and a temporary raw store, so they need no network or credentials. Add focused tests alongside quality and idempotency behavior as those features are implemented.

## Continuous integration

After `make hooks`, [a pre-push hook](../.githooks/pre-push) runs `make check` before each push. It checks the working tree, so commit or stash other changes first.

[The check workflow](../.github/workflows/check.yml) runs `make check` on every pull request.

## Dependencies

Add or remove direct dependencies with uv and exact versions, then commit both `pyproject.toml` and the updated `uv.lock`. Use `uv sync --locked` for normal setup so dependency drift is reported instead of silently changing the environment.

```sh
uv add "package==x.y.z"
uv add --dev "tool==x.y.z"
uv lock
```

Update uv and Ruff only after checking their current release notes and compatibility. The project requires uv 0.13.1 or later in the 0.13 series; update `tool.uv.required-version` together with the lockfile when adopting another series.
