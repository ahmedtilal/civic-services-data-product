import logging
import re

from typer.testing import CliRunner

from civic_service_requests import cli


def invoke(*args: str):
    return CliRunner().invoke(cli.app, ["land-raw", *args])


def test_help_works_without_credentials():
    result = invoke("--help")

    assert result.exit_code == 0
    # Typer forces colour on GitHub Actions, which splits option names.
    assert "--retries" in re.sub(r"\x1b\[[0-9;]*m", "", result.output)


def test_invalid_window_exits_2_with_the_reason():
    result = invoke("--start", "2025-01-08", "--end", "2025-01-08")

    assert result.exit_code == 2
    assert "Invalid options: window_end must be after window_start" in result.output


def test_stopped_run_exits_1_and_reports_it_incomplete(monkeypatch, make_source, tmp_path):
    monkeypatch.setattr(cli, "NycOpenDataSource", lambda: make_source([1], fail_pages={0: 1}))

    result = invoke("--raw-dir", str(tmp_path))

    assert result.exit_code == 1
    assert "is incomplete: ConnectionError" in result.output


def test_complete_run_reports_its_size_and_silences_request_urls(
    monkeypatch, make_source, tmp_path
):
    monkeypatch.setattr(cli, "NycOpenDataSource", lambda: make_source([1]))

    result = invoke("--raw-dir", str(tmp_path))

    assert result.exit_code == 0
    assert "1 rows in 1 page\n" in result.output
    assert not logging.getLogger("httpx").isEnabledFor(logging.INFO)
