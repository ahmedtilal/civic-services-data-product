# Coding standards

Judgement calls that `make check` cannot enforce. A breach is a review finding to fix, not an optional note.

## Comments and docstrings

- Write one only for what the code cannot show: a reason, a constraint, or a contract an implementer must honour (for example on a `Protocol` method). Names and types carry the rest.
- Modules and classes need no docstring by default. Typer command docstrings are `--help` text, so keep them.
- Explain a Pydantic field with `Field(description=...)`.

## Defaults and types

- A default used in more than one place is a named constant, imported by each user. Reaching into `model_fields` to recover one loses type checking.
- Narrow optionals with `is not None`, so the type checker can follow.
- Fix type errors in the code. A `# type: ignore[<rule>]` names its rule and is for input a validator converts at runtime.

- A string that links two places, such as a pipeline's input and output keys, is a named constant.

## Libraries

- Before writing parsing or data handling by hand, use a library that the project has or that the [roadmap](docs/roadmap.md) will bring in. Tabular data, including CSV, goes through Polars.

## Module boundaries

- Each module has one responsibility and a small interface. Step functions live in their step module; `pipeline.py` only wires and runs them. The layout is in [AGENTS.md](AGENTS.md#architecture-constraints).

## Tests

- **Mirror the source:** `src/civic_service_requests/<path>/<name>.py` is tested in `tests/<path>/test_<name>.py`. Shared fakes and fixtures sit in `conftest.py`.
- **Pyramid:** test each behaviour at the lowest level that can catch its regression. Most tests are unit tests of one module, a few run a whole pipeline, and the CLI tests cover only what the CLI decides (exit codes, messages).
- **Earn its place:** each test names a regression it would catch. Behaviour owned by a library, restated constants and cases already covered lower down need no test.
- **Boundaries:** fake only the source and the network. Use a real store in a temporary directory.
- **Pipeline wiring:** in a module-scoped fixture, run `pipeline.to_testable(reads=...)` once, with every read step replaced and writes captured. Assert each dataset in `result.catalog`, and the write inputs in `result.written`, in its own test.
