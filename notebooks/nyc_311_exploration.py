# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo==0.25.2",
#     "polars==2.1.0",
#     "requests==2.34.2",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Exploring NYC 311 before building

        This notebook reads a bounded sample of the NYC Open Data 311 dataset
        (`erm2-nwe9`). It only reads from the source: it writes nothing to disk and needs
        no cloud credentials. Run it with:

        ```sh
        uvx marimo edit --sandbox notebooks/nyc_311_exploration.py
        ```

        Every number below is a measurement from the moment you run it. The source changes
        daily and can revise older rows, so a repeated run may differ.
        """
    )
    return (mo,)


@app.cell
def _():
    import csv
    from datetime import date, timedelta
    from io import BytesIO, StringIO

    import polars as pl
    import requests

    JSON_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    CSV_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
    COLUMNS_URL = "https://data.cityofnewyork.us/api/views/erm2-nwe9/columns.json"

    WINDOW_START = date(2025, 1, 1)  # inclusive
    WINDOW_END = date(2025, 1, 8)  # exclusive
    SAMPLE_PER_DAY = 200
    PAGE_SIZE = 10_000

    # The source fields behind the draft output contract (see docs/data-product.md).
    CONTRACT_FIELDS = [
        "unique_key",
        "created_date",
        "closed_date",
        "agency",
        "complaint_type",
        "descriptor",
        "status",
        "borough",
        "latitude",
        "longitude",
    ]

    def where_clause(start: date, end_exclusive: date) -> str:
        return f"created_date >= '{start}T00:00:00' AND created_date < '{end_exclusive}T00:00:00'"

    WINDOW = where_clause(WINDOW_START, WINDOW_END)
    return (
        BytesIO,
        COLUMNS_URL,
        CONTRACT_FIELDS,
        CSV_URL,
        JSON_URL,
        PAGE_SIZE,
        SAMPLE_PER_DAY,
        WINDOW,
        WINDOW_END,
        WINDOW_START,
        StringIO,
        csv,
        pl,
        requests,
        timedelta,
        where_clause,
    )


@app.cell
def _(JSON_URL, WINDOW, mo, requests):
    # Volume: ask the source to count, without downloading rows.
    _response = requests.get(JSON_URL, params={"$select": "count(*)", "$where": WINDOW}, timeout=30)
    _response.raise_for_status()
    week_count = int(_response.json()[0]["count"])
    mo.md(f"**Rows created in the window:** {week_count:,}")
    return (week_count,)


@app.cell
def _(
    BytesIO,
    CSV_URL,
    SAMPLE_PER_DAY,
    WINDOW_END,
    WINDOW_START,
    pl,
    requests,
    timedelta,
    where_clause,
):
    # Sample: a few rows from each day, ordered so the sample is repeatable.
    _frames = []
    sample_bytes = 0
    _day = WINDOW_START
    while _day < WINDOW_END:
        _result = requests.get(
            CSV_URL,
            params={
                "$where": where_clause(_day, _day + timedelta(days=1)),
                "$order": "created_date, unique_key",
                "$limit": SAMPLE_PER_DAY,
            },
            timeout=30,
        )
        _result.raise_for_status()
        sample_bytes += len(_result.content)
        _frames.append(pl.read_csv(BytesIO(_result.content)))
        _day += timedelta(days=1)

    sample = pl.concat(_frames, how="diagonal_relaxed")
    return sample, sample_bytes


@app.cell
def _(CONTRACT_FIELDS, mo, sample):
    # Look at actual rows before computing anything about them.
    mo.vstack(
        [
            mo.md(
                "## A look at the rows\n\n"
                "Ten rows from the sample, showing the fields our draft contract uses. "
                "Each row should be one service request. Use the table's column menu to "
                "search, sort, or open a row; the sample has more columns than these."
            ),
            mo.ui.table(sample.select(CONTRACT_FIELDS).head(10), selection=None),
            mo.md(
                "The same rows with every column, transposed so each request reads top to bottom:"
            ),
            mo.ui.table(
                sample.head(3).transpose(
                    include_header=True,
                    header_name="field",
                    column_names=[f"row {i + 1}" for i in range(3)],
                ),
                selection=None,
                page_size=50,
            ),
        ]
    )
    return


@app.cell
def _(mo, sample):
    mo.vstack(
        [
            mo.md(f"## Shape\n\n{sample.height:,} rows x {sample.width} columns"),
            mo.md("## Schema (as inferred by Polars)"),
            mo.ui.table(
                [{"column": name, "type": str(dtype)} for name, dtype in sample.schema.items()],
                selection=None,
            ),
        ]
    )
    return


@app.cell
def _(COLUMNS_URL, CONTRACT_FIELDS, mo, requests, sample):
    # Compare the sample's columns with the source's own metadata. The portal's labels
    # (for example "Problem") can differ from the API field names (`complaint_type`).
    _metadata = requests.get(COLUMNS_URL, timeout=30)
    _metadata.raise_for_status()
    _labels = {c["fieldName"]: c["name"] for c in _metadata.json()}
    _rows = [
        {
            "api field": name,
            "portal label": _labels.get(name, "(not in metadata)"),
        }
        for name in sample.columns
    ]
    mo.vstack(
        [
            mo.md(
                "## Field names\n\nThe fields our requirements use, with the portal's label for each."
            ),
            mo.ui.table(
                [row for row in _rows if row["api field"] in CONTRACT_FIELDS],
                selection=None,
            ),
        ]
    )
    return


@app.cell
def _(CONTRACT_FIELDS, mo, pl, sample):
    # Which fields can be empty? Null rates for the fields in the draft contract.
    _missing = [f for f in CONTRACT_FIELDS if f not in sample.columns]
    null_rates = sample.select(
        [
            (pl.col(f).null_count() / pl.len()).alias(f)
            for f in CONTRACT_FIELDS
            if f in sample.columns
        ]
    ).transpose(include_header=True, header_name="field", column_names=["null_rate"])
    mo.vstack(
        [
            mo.md(
                "## Null rates in the sample\n\n"
                + (
                    f"**Missing columns:** {_missing}\n\n"
                    if _missing
                    else "All requirement fields are present.\n\n"
                )
                + "A sample can show a field *can* be empty. It cannot show a field is never empty."
            ),
            mo.ui.table(null_rates.to_dicts(), selection=None),
        ]
    )
    return


@app.cell
def _(mo, pl, sample):
    # Are categories open-ended? Count distinct values and show the most common.
    _top_categories = sample.group_by("complaint_type").len().sort("len", descending=True).head(10)
    mo.vstack(
        [
            mo.md(
                f"""
                ## Categories and one-row-one-request

                - Distinct `complaint_type` values in the sample: **{sample["complaint_type"].n_unique()}**
                - Distinct `borough` values: **{sample["borough"].unique().sort().to_list()}**
                - Distinct `status` values: **{sample["status"].unique().sort().to_list()}**
                - Duplicate `unique_key` values in the sample: **{sample.height - sample["unique_key"].n_unique()}**

                A clean sample does not prove `unique_key` is unique across the whole window. That
                becomes a check in the pipeline.
                """
            ),
            mo.ui.table(_top_categories.to_dicts(), selection=None),
        ]
    )
    return


@app.cell
def _(mo, sample, sample_bytes, week_count):
    # A rough size estimate, scaled up from the sample. This is an estimate, not a measurement:
    # the sample is the first rows of each day, which may differ from the rest.
    _bytes_per_row = sample_bytes / sample.height
    estimated_bytes = _bytes_per_row * week_count
    mo.md(
        f"""
        ## Rough extract size

        - Sample: {sample.height:,} rows, {sample_bytes:,} bytes ({_bytes_per_row:,.0f} bytes per row)
        - Window rows: {week_count:,}
        - **Estimated** CSV size for the window: about {estimated_bytes / 1_000_000:,.0f} MB

        Treat the estimate as a planning number. The next switch measures it.
        """
    )
    return


@app.cell
def _(mo):
    measure = mo.ui.switch(label="Download every page of the window to measure its size")
    mo.vstack(
        [
            mo.md(
                "Measuring downloads the whole window in pages of 10,000 rows and keeps only "
                "the counts. It writes nothing to disk, but it makes several requests and "
                "transfers the full extract."
            ),
            measure,
        ]
    )
    return (measure,)


@app.cell
def _(CSV_URL, PAGE_SIZE, WINDOW, StringIO, csv, measure, mo, requests):
    mo.stop(not measure.value, mo.md("*Switch on to measure.*"))

    _offset = 0
    measured_pages = 0
    measured_bytes = 0
    measured_rows = 0
    while True:
        _page = requests.get(
            CSV_URL,
            params={
                "$where": WINDOW,
                "$order": "unique_key",
                "$limit": PAGE_SIZE,
                "$offset": _offset,
            },
            timeout=60,
        )
        _page.raise_for_status()
        # Count CSV records, not lines: quoted fields can contain line breaks.
        _records = sum(1 for _ in csv.reader(StringIO(_page.text))) - 1
        if _records <= 0:
            break
        measured_pages += 1
        measured_bytes += len(_page.content)
        measured_rows += _records
        if _records < PAGE_SIZE:
            break
        _offset += PAGE_SIZE

    mo.md(
        f"""
        ## Measured extract

        - Pages: **{measured_pages}**
        - Rows: **{measured_rows:,}**
        - CSV bytes: **{measured_bytes:,}** ({measured_bytes / 1_000_000:,.1f} MB)

        Record these with the date you measured them. The source can change.
        """
    )
    return


if __name__ == "__main__":
    app.run()
