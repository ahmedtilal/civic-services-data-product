UV ?= uv

.PHONY: help sync run lint format format-check check clean

help:
	@echo "sync          Install the locked project environment"
	@echo "run           Show civic-data CLI help"
	@echo "lint          Run Ruff lint checks"
	@echo "format        Format Python files with Ruff"
	@echo "format-check  Check Ruff formatting without changing files"
	@echo "check         Run lint and formatting checks"
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

check: lint format-check

clean:
	rm -rf .venv .ruff_cache .mypy_cache .pytest_cache build dist *.egg-info
