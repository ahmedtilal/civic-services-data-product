"""Command-line entry point for the Civic Service Requests project."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from masoora import StepExecutionError
from pydantic import ValidationError

from civic_service_requests import __version__
from civic_service_requests.pipelines import land_raw
from civic_service_requests.pipelines.land_raw.context import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_RETRIES,
    DEFAULT_WINDOW_END,
    DEFAULT_WINDOW_START,
)
from civic_service_requests.raw_store import DEFAULT_RAW_DIR, LocalRawStore
from civic_service_requests.source import NycOpenDataSource

app = typer.Typer(
    name="civic-data",
    help="Build and operate the Civic Service Requests data product.",
    no_args_is_help=True,
)


@app.command()
def about() -> None:
    """Show the product and current implementation checkpoint."""
    typer.echo("Civic Service Requests (civic_service_requests)")
    typer.echo("Series: Build a Data Platform on a Budget")
    typer.echo("Checkpoint: project scaffold")


@app.command()
def version() -> None:
    """Show the installed CLI version."""
    typer.echo(__version__)


@app.command("land-raw")
def land_raw_command(
    start: Annotated[
        str, typer.Option(help="First created date in the batch (YYYY-MM-DD).")
    ] = DEFAULT_WINDOW_START.isoformat(),
    end: Annotated[
        str, typer.Option(help="Created date after the batch (YYYY-MM-DD, exclusive).")
    ] = DEFAULT_WINDOW_END.isoformat(),
    page_size: Annotated[int, typer.Option(help="Rows per CSV page.")] = DEFAULT_PAGE_SIZE,
    retries: Annotated[
        int, typer.Option(help="Retries per page before the run stops.")
    ] = DEFAULT_RETRIES,
    raw_dir: Annotated[Path, typer.Option(help="Local raw store root.")] = DEFAULT_RAW_DIR,
) -> None:
    """Land one batch of NYC 311 source pages and a manifest in the local raw store."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # httpx logs each request URL at INFO; run logs carry only run facts.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        context = land_raw.LandRawContext(
            window_start=start,  # type: ignore[bad-argument-type]
            window_end=end,  # type: ignore[bad-argument-type]
            page_size=page_size,
            retries=retries,
        )
    except ValidationError as exc:
        for error in exc.errors():
            option = ".".join(map(str, error["loc"]))
            label = f"Invalid option {option}" if option else "Invalid options"
            typer.echo(f"{label}: {error['msg'].removeprefix('Value error, ')}", err=True)
        raise typer.Exit(2) from exc

    source = NycOpenDataSource()
    try:
        manifest = land_raw.run(context, source, LocalRawStore(raw_dir))
    except StepExecutionError as exc:
        typer.echo(
            f"Run {context.run_id} is incomplete: {type(exc.original).__name__}: {exc.original}",
            err=True,
        )
        raise typer.Exit(1) from exc
    finally:
        source.close()
    pages = len(manifest.pages)
    typer.echo(
        f"Run {manifest.run_id} complete: {manifest.total_rows} rows "
        f"in {pages} {'page' if pages == 1 else 'pages'}"
    )


def main() -> None:
    """Run the civic-data command-line application."""
    app()
