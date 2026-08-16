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


if __name__ == "__main__":
    app()
