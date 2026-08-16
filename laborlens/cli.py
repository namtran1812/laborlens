from __future__ import annotations

import asyncio
from datetime import date

import typer

from laborlens.analysis.features import SeriesPoint, anomalies, compute_features
from laborlens.config import get_settings
from laborlens.data.fred import FredClient
from laborlens.services.ingestion import IngestionService
from laborlens.storage.clickhouse import ClickHouseStore

app = typer.Typer(
    no_args_is_help=True,
    help="LaborLens economic data CLI",
)


def build_service() -> IngestionService:
    settings = get_settings()

    return IngestionService(
        FredClient(settings.fred_api_key),
        ClickHouseStore(settings),
    )


@app.command()
def ingest(
    series_id: str,
    from_date: str | None = typer.Option(
        None,
        "--from",
    ),
    to_date: str | None = typer.Option(
        None,
        "--to",
    ),
) -> None:
    start = date.fromisoformat(from_date) if from_date else None

    end = date.fromisoformat(to_date) if to_date else None

    count = asyncio.run(
        build_service().ingest_latest(
            series_id,
            observation_start=start,
            observation_end=end,
        )
    )

    typer.echo(f"ingested {count} rows for {series_id.upper()}")


@app.command()
def vintage(
    series_id: str,
    dates: str = typer.Option(
        ...,
        "--dates",
        help=("Comma-separated vintage dates in YYYY-MM-DD format"),
    ),
    from_date: str | None = typer.Option(
        None,
        "--from",
    ),
    to_date: str | None = typer.Option(
        None,
        "--to",
    ),
) -> None:
    vintage_dates = [
        date.fromisoformat(value.strip()) for value in dates.split(",") if value.strip()
    ]

    start = date.fromisoformat(from_date) if from_date else None

    end = date.fromisoformat(to_date) if to_date else None

    count = asyncio.run(
        build_service().ingest_vintages(
            series_id,
            vintage_dates=vintage_dates,
            observation_start=start,
            observation_end=end,
        )
    )

    typer.echo(f"ingested {count} vintage rows for {series_id.upper()}")


@app.command("as-of")
def as_of(
    series_id: str,
    query_date: str = typer.Option(
        ...,
        "--date",
    ),
) -> None:
    store = ClickHouseStore(get_settings())

    rows = store.as_of(
        series_id.upper(),
        date.fromisoformat(query_date),
    )

    for row in rows:
        typer.echo(f"{row[0]}\t{row[1]}\t{row[2]}..{row[3]}")


@app.command()
def analyze(
    series_id: str,
    query_date: str | None = typer.Option(
        None,
        "--date",
        help="Historical information date.",
    ),
    latest: bool = typer.Option(
        False,
        "--latest",
        help="Use the newest stored vintage.",
    ),
    window: int = typer.Option(
        12,
        "--window",
    ),
    threshold: float = typer.Option(
        2.0,
        "--threshold",
    ),
) -> None:
    store = ClickHouseStore(get_settings())

    if latest and query_date is not None:
        raise typer.BadParameter("use either --latest or --date, not both")

    if latest:
        resolved_date = store.latest_vintage_date(series_id.upper())

        if resolved_date is None:
            raise typer.BadParameter(f"no observations stored for {series_id.upper()}")

    elif query_date is not None:
        resolved_date = date.fromisoformat(query_date)

    else:
        raise typer.BadParameter("provide either --date YYYY-MM-DD or --latest")

    rows = store.as_of(
        series_id.upper(),
        resolved_date,
    )

    points = [
        SeriesPoint(
            observation_date=row[0],
            value=float(row[1]),
        )
        for row in rows
        if row[1] is not None
    ]

    features = compute_features(
        points,
        rolling_window=window,
    )

    flagged = anomalies(
        features,
        threshold=threshold,
    )

    typer.echo(f"series={series_id.upper()}")
    typer.echo(f"as_of={resolved_date}")
    typer.echo(f"observations={len(points)}")
    typer.echo(f"anomalies={len(flagged)}")
    typer.echo("")

    for point in flagged:
        delta1 = f"{point.delta_1:.4f}" if point.delta_1 is not None else "None"

        acceleration = f"{point.acceleration:.4f}" if point.acceleration is not None else "None"

        typer.echo(
            f"{point.observation_date}\t"
            f"value={point.value:.4f}\t"
            f"z={point.z_score:.3f}\t"
            f"delta1={delta1}\t"
            f"accel={acceleration}"
        )


@app.command()
def compare(
    left_series: str,
    right_series: str,
    query_date: str | None = typer.Option(
        None,
        "--date",
        help="Use a shared historical information date.",
    ),
    latest: bool = typer.Option(
        False,
        "--latest",
        help="Use each series' newest stored vintage.",
    ),
    window: int = typer.Option(
        12,
        "--window",
    ),
    threshold: float = typer.Option(
        2.0,
        "--threshold",
    ),
) -> None:
    from laborlens.analysis.divergence import (
        align_series,
        compute_divergence,
        divergence_anomalies,
    )

    left_series = left_series.upper()
    right_series = right_series.upper()

    if latest and query_date is not None:
        raise typer.BadParameter("use either --latest or --date, not both")

    if not latest and query_date is None:
        raise typer.BadParameter("provide either --date YYYY-MM-DD or --latest")

    store = ClickHouseStore(get_settings())

    if latest:
        left_date = store.latest_vintage_date(left_series)

        right_date = store.latest_vintage_date(right_series)

        if left_date is None:
            raise typer.BadParameter(f"no observations stored for {left_series}")

        if right_date is None:
            raise typer.BadParameter(f"no observations stored for {right_series}")

    else:
        shared_date = date.fromisoformat(query_date)

        left_date = shared_date
        right_date = shared_date

    left_rows = store.as_of(
        left_series,
        left_date,
    )

    right_rows = store.as_of(
        right_series,
        right_date,
    )

    left = [
        (
            row[0],
            float(row[1]),
        )
        for row in left_rows
        if row[1] is not None
    ]

    right = [
        (
            row[0],
            float(row[1]),
        )
        for row in right_rows
        if row[1] is not None
    ]

    aligned = align_series(
        left,
        right,
    )

    results = compute_divergence(
        aligned,
        window=window,
    )

    flagged = divergence_anomalies(
        results,
        threshold=threshold,
    )

    typer.echo(f"left={left_series}")

    typer.echo(f"right={right_series}")

    typer.echo(f"left_as_of={left_date}")

    typer.echo(f"right_as_of={right_date}")

    typer.echo(f"aligned_observations={len(aligned)}")

    typer.echo(f"divergence_anomalies={len(flagged)}")

    typer.echo("")

    for point in flagged:
        left_change = f"{point.left_change:.4%}" if point.left_change is not None else "None"

        right_change = f"{point.right_change:.4%}" if point.right_change is not None else "None"

        left_z = f"{point.left_change_z:.3f}" if point.left_change_z is not None else "None"

        right_z = f"{point.right_change_z:.3f}" if point.right_change_z is not None else "None"

        divergence = f"{point.divergence:.3f}" if point.divergence is not None else "None"

        correlation = f"{point.correlation:.3f}" if point.correlation is not None else "None"

        typer.echo(
            f"{point.observation_date}\t"
            f"{left_series}_change={left_change}\t"
            f"{right_series}_change={right_change}\t"
            f"{left_series}_z={left_z}\t"
            f"{right_series}_z={right_z}\t"
            f"div={divergence}\t"
            f"corr={correlation}"
        )


if __name__ == "__main__":
    app()
