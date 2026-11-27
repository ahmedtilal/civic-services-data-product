UV ?= uv

.PHONY: help sync run lint format format-check typecheck test check hooks clean

help:
	@echo "sync          Install the locked project environment"
	@echo "run           Show civic-data CLI help"
	@echo "lint          Run Ruff lint checks"
	@echo "format        Format Python files with Ruff"
	@echo "format-check  Check Ruff formatting without changing files"
	@echo "test          Run the pytest suite"
	@echo "typecheck     Run Pyrefly type checks"
	@echo "check         Run lint, format, type checks, and tests"
	@echo "hooks         Enable the Git pre-push hook"
	@echo "clean         Remove local build and cache output"

sync:
	$(UV) sync --locked

run:
	$(UV) run --locked civic-data

lint:
	$(UV) run --locked ruff check .

format:
	$(UV) run --locked ruff format .

format-check:
	$(UV) run --locked ruff format --check .

test:
	$(UV) run --locked pytest

typecheck:
	$(UV) run --locked pyrefly check

check: lint format-check typecheck test

hooks:
	git config core.hooksPath .githooks

clean:
	rm -rf .venv .ruff_cache .mypy_cache .pytest_cache build dist *.egg-info
