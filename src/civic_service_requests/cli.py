"""Command-line entry point for the Civic Service Requests project."""

import typer

from civic_service_requests import __version__

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


def main() -> None:
    """Run the civic-data command-line application."""
    app()
