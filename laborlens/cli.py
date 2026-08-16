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
        help="Use the newest stored snapshot.",
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
        rows = store.latest_snapshot(series_id.upper())

        if not rows:
            raise typer.BadParameter(f"no observations stored for {series_id.upper()}")

        resolved_date = max(row[2] for row in rows)

    elif query_date is not None:
        resolved_date = date.fromisoformat(query_date)

        rows = store.as_of(
            series_id.upper(),
            resolved_date,
        )

    else:
        raise typer.BadParameter("provide either --date YYYY-MM-DD or --latest")

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
        help="Use the newest stored snapshot for each series.",
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
        left_rows = store.latest_snapshot(left_series)

        right_rows = store.latest_snapshot(right_series)

        if not left_rows:
            raise typer.BadParameter(f"no observations stored for {left_series}")

        if not right_rows:
            raise typer.BadParameter(f"no observations stored for {right_series}")

        left_date = max(row[2] for row in left_rows)

        right_date = max(row[2] for row in right_rows)

    else:
        shared_date = date.fromisoformat(query_date)

        left_date = shared_date
        right_date = shared_date

        left_rows = store.as_of(
            left_series,
            shared_date,
        )

        right_rows = store.as_of(
            right_series,
            shared_date,
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


@app.command()
def regime(
    window: int = typer.Option(
        24,
        "--window",
        help="Rolling window used to normalize each signal.",
    ),
    limit: int = typer.Option(
        36,
        "--limit",
        help="Number of most recent regime observations to print.",
    ),
) -> None:
    from laborlens.analysis.regime import (
        DEFAULT_SPECS,
        compute_regime,
        compute_signal,
    )

    store = ClickHouseStore(get_settings())

    signals = {}

    for series_id, spec in DEFAULT_SPECS.items():
        rows = store.latest_snapshot(series_id)

        if not rows:
            typer.echo(f"warning: no data for {series_id}")
            continue

        points = [
            (
                row[0],
                float(row[1]),
            )
            for row in rows
            if row[1] is not None
        ]

        signals[series_id] = compute_signal(
            points,
            spec,
            window=window,
        )

    regimes = compute_regime(signals)

    typer.echo(f"window={window}")

    typer.echo(f"signals={','.join(signals)}")

    typer.echo(f"regime_observations={len(regimes)}")

    typer.echo("")

    for point in regimes[-limit:]:
        contributions = " ".join(
            f"{series}={value:.2f}" for series, value in sorted(point.contributions.items())
        )

        typer.echo(
            f"{point.observation_date}\t"
            f"raw={point.raw_score:.3f}\t"
            f"score={point.score:.3f}\t"
            f"dispersion={point.dispersion:.3f}\t"
            f"coverage={point.coverage:.0%}\t"
            f"label={point.label}\t"
            f"signals={point.signals_used}\t"
            f"{contributions}"
        )


@app.command()
def claims(
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
    ),
) -> None:
    from laborlens.analysis.regime import (
        DEFAULT_SPECS,
        compute_regime,
        compute_signal,
    )
    from laborlens.research.claims import (
        discover_claims,
    )

    store = ClickHouseStore(get_settings())

    signals = {}

    for series_id, spec in DEFAULT_SPECS.items():
        rows = store.latest_snapshot(series_id)

        if not rows:
            continue

        points = [
            (
                row[0],
                float(row[1]),
            )
            for row in rows
            if row[1] is not None
        ]

        signals[series_id] = compute_signal(
            points,
            spec,
            window=window,
        )

    regimes = compute_regime(signals)

    candidates = discover_claims(
        regimes,
        min_confidence=min_confidence,
    )

    typer.echo(f"window={window}")

    typer.echo(f"min_confidence={min_confidence:.2f}")

    typer.echo(f"claims={len(candidates)}")

    typer.echo("")

    for claim in candidates[-limit:]:
        typer.echo(
            f"{claim.observation_date}\t"
            f"type={claim.claim_type}\t"
            f"confidence="
            f"{claim.confidence:.3f}\t"
            f"score={claim.score:.3f}\t"
            f"dispersion="
            f"{claim.dispersion:.3f}\t"
            f"coverage="
            f"{claim.coverage:.0%}"
        )

        typer.echo(f"  {claim.headline}")

        evidence = " ".join(f"{item.series_id}={item.contribution:.2f}" for item in claim.evidence)

        typer.echo(f"  evidence: {evidence}")

        typer.echo("")


@app.command()
def episodes(
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
    ),
) -> None:
    from laborlens.analysis.regime import (
        DEFAULT_SPECS,
        compute_regime,
        compute_signal,
    )
    from laborlens.research.claims import (
        discover_claims,
    )
    from laborlens.research.episodes import (
        cluster_claims,
    )

    store = ClickHouseStore(get_settings())

    signals = {}

    for series_id, spec in DEFAULT_SPECS.items():
        rows = store.latest_snapshot(series_id)

        if not rows:
            continue

        points = [
            (
                row[0],
                float(row[1]),
            )
            for row in rows
            if row[1] is not None
        ]

        signals[series_id] = compute_signal(
            points,
            spec,
            window=window,
        )

    regimes = compute_regime(signals)

    candidates = discover_claims(
        regimes,
        min_confidence=min_confidence,
    )

    grouped = cluster_claims(candidates)

    typer.echo(f"claims={len(candidates)}")
    typer.echo(f"episodes={len(grouped)}")
    typer.echo("")

    ranked = sorted(
        grouped,
        key=lambda episode: (
            episode.peak_confidence,
            episode.duration_months,
        ),
        reverse=True,
    )

    for episode in ranked[:limit]:
        claim = episode.representative

        typer.echo(
            f"{episode.start_date}"
            f"..{episode.end_date}\t"
            f"type={episode.claim_type}\t"
            f"months={episode.duration_months}\t"
            f"peak_confidence="
            f"{episode.peak_confidence:.3f}"
        )

        typer.echo(f"  representative={claim.observation_date}")

        typer.echo(f"  {claim.headline}")

        evidence = " ".join(f"{item.series_id}={item.contribution:.2f}" for item in claim.evidence)

        typer.echo(f"  evidence: {evidence}")

        typer.echo("")


@app.command()
def review(
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
    ),
) -> None:
    from laborlens.analysis.regime import (
        DEFAULT_SPECS,
        compute_regime,
        compute_signal,
    )
    from laborlens.research.claims import (
        discover_claims,
    )
    from laborlens.research.episodes import (
        cluster_claims,
    )
    from laborlens.research.evidence import (
        build_evidence_bundle,
    )
    from laborlens.research.skeptic import (
        review_evidence,
    )

    store = ClickHouseStore(get_settings())

    signals = {}

    for series_id, spec in DEFAULT_SPECS.items():
        rows = store.latest_snapshot(series_id)

        if not rows:
            continue

        points = [
            (
                row[0],
                float(row[1]),
            )
            for row in rows
            if row[1] is not None
        ]

        signals[series_id] = compute_signal(
            points,
            spec,
            window=window,
        )

    regimes = compute_regime(signals)

    candidates = discover_claims(
        regimes,
        min_confidence=min_confidence,
    )

    episodes = cluster_claims(candidates)

    reviewed = []

    for episode in episodes:
        bundle = build_evidence_bundle(episode)

        verdict = review_evidence(bundle)

        reviewed.append(
            (
                episode,
                bundle,
                verdict,
            )
        )

    reviewed.sort(
        key=lambda item: (
            item[2].score,
            item[0].peak_confidence,
            item[0].duration_months,
        ),
        reverse=True,
    )

    typer.echo(f"claims={len(candidates)}")

    typer.echo(f"episodes={len(episodes)}")

    typer.echo(f"reviewed={len(reviewed)}")

    typer.echo("")

    for (
        episode,
        bundle,
        verdict,
    ) in reviewed[:limit]:
        typer.echo(
            f"{episode.start_date}"
            f"..{episode.end_date}\t"
            f"type={episode.claim_type}\t"
            f"verdict={verdict.verdict}\t"
            f"review_score="
            f"{verdict.score:.3f}\t"
            f"claim_confidence="
            f"{bundle.confidence:.3f}\t"
            f"breadth="
            f"{bundle.breadth:.0%}"
        )

        typer.echo(f"  hypothesis: {bundle.headline}")

        if bundle.supporting:
            support = " ".join(
                f"{item.series_id}={item.contribution:.2f}" for item in bundle.supporting
            )

            typer.echo(f"  support: {support}")

        else:
            typer.echo("  support: none")

        if bundle.opposing:
            opposition = " ".join(
                f"{item.series_id}={item.contribution:.2f}" for item in bundle.opposing
            )

            typer.echo(f"  counter: {opposition}")

        else:
            typer.echo("  counter: none")

        if verdict.findings:
            for finding in verdict.findings:
                typer.echo(f"  finding: [{finding.severity}] {finding.code} - {finding.message}")

        else:
            typer.echo("  findings: none")

        typer.echo("")


@app.command()
def bundle(
    start: str = typer.Option(
        ...,
        "--start",
        help="Episode start date YYYY-MM-DD.",
    ),
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
) -> None:
    from laborlens.analysis.regime import (
        DEFAULT_SPECS,
        compute_regime,
        compute_signal,
    )
    from laborlens.research.claims import (
        discover_claims,
    )
    from laborlens.research.episodes import (
        cluster_claims,
    )
    from laborlens.research.evidence import (
        build_evidence_bundle,
    )
    from laborlens.research.research_bundle import (
        ProvenanceItem,
        build_research_bundle,
    )
    from laborlens.research.skeptic import (
        review_evidence,
    )

    store = ClickHouseStore(get_settings())

    signals = {}

    for series_id, spec in DEFAULT_SPECS.items():
        rows = store.latest_snapshot(series_id)

        if not rows:
            continue

        points = [
            (
                row[0],
                float(row[1]),
            )
            for row in rows
            if row[1] is not None
        ]

        signals[series_id] = compute_signal(
            points,
            spec,
            window=window,
        )

    regimes = compute_regime(signals)

    claims = discover_claims(
        regimes,
        min_confidence=min_confidence,
    )

    episodes = cluster_claims(claims)

    target_date = date.fromisoformat(start)

    matches = [episode for episode in episodes if episode.start_date == target_date]

    if not matches:
        raise typer.BadParameter(f"no episode starts on {start}")

    episode = matches[0]

    evidence = build_evidence_bundle(episode)

    skeptic = review_evidence(evidence)

    provenance = []

    for series_id in DEFAULT_SPECS:
        rows = store.provenance_for_window(
            series_id,
            episode.start_date,
            episode.end_date,
        )

        for row in rows:
            if row[1] is None:
                continue

            provenance.append(
                ProvenanceItem(
                    series_id=series_id,
                    observation_date=row[0],
                    value=float(row[1]),
                    realtime_start=row[2],
                    realtime_end=row[3],
                )
            )

    research = build_research_bundle(
        episode=episode,
        evidence=evidence,
        skeptic=skeptic,
        regimes=regimes,
        all_episodes=episodes,
        provenance=provenance,
    )

    typer.echo(f"episode={research.episode_id}")

    typer.echo(f"period={research.episode.start_date}..{research.episode.end_date}")

    typer.echo(f"claim={research.claim.headline}")

    typer.echo(f"verdict={research.skeptic.verdict}")

    typer.echo(f"review_score={research.skeptic.score:.3f}")

    typer.echo(f"historical_percentile={research.historical_percentile:.1%}")

    typer.echo(f"mean_episode_score={research.mean_episode_score:.3f}")

    typer.echo(f"peak_episode_score={research.peak_episode_score:.3f}")

    typer.echo("")

    typer.echo("support:")

    for item in research.evidence.supporting:
        typer.echo(f"  {item.series_id}: {item.contribution:.3f}")

    typer.echo("")

    typer.echo("counter:")

    if research.evidence.opposing:
        for item in research.evidence.opposing:
            typer.echo(f"  {item.series_id}: {item.contribution:.3f}")
    else:
        typer.echo("  none")

    typer.echo("")

    typer.echo("historical_analogs:")

    if research.historical_analogs:
        for analog in research.historical_analogs:
            typer.echo(
                f"  {analog.start_date}"
                f"..{analog.end_date} "
                f"score={analog.score:.3f} "
                f"confidence="
                f"{analog.confidence:.3f}"
            )
    else:
        typer.echo("  none")

    typer.echo("")

    typer.echo(f"provenance_rows={len(research.provenance)}")


@app.command()
def article(
    start: str = typer.Option(
        ...,
        "--start",
        help="Episode start date YYYY-MM-DD.",
    ),
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
    verify: bool = typer.Option(
        True,
        "--verify/--no-verify",
        help=("Verify generated numerical claims against the bundle."),
    ),
) -> None:
    from laborlens.services.research_pipeline import (
        ResearchPipeline,
    )
    from laborlens.writer.deterministic_writer import (
        write_deterministic_article,
    )
    from laborlens.writer.verifier import (
        verify_article_numbers,
    )

    settings = get_settings()

    store = ClickHouseStore(settings)

    pipeline = ResearchPipeline(store)

    try:
        research = pipeline.build(
            start_date=date.fromisoformat(start),
            window=window,
            min_confidence=min_confidence,
        )

    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if research.skeptic.verdict != "supported":
        typer.echo("Article generation blocked.")

        typer.echo(f"Reason: research episode verdict is {research.skeptic.verdict}.")

        raise typer.Exit(code=2)

    typer.echo(f"episode={research.episode_id}")

    typer.echo("writer=deterministic")

    draft = write_deterministic_article(research)

    if verify:
        result = verify_article_numbers(
            draft,
            research,
        )

        typer.echo("")

        typer.echo("verification=" + ("PASSED" if result.passed else "REJECTED"))

        if result.unsupported_dates:
            typer.echo("unsupported_dates=" + ",".join(result.unsupported_dates))

        if result.unsupported_numbers:
            typer.echo("unsupported_numbers=" + ",".join(result.unsupported_numbers))

        if not result.passed:
            typer.echo("")
            typer.echo("Draft rejected. It is shown below only for debugging.")

    typer.echo("")
    typer.echo("----- ARTICLE -----")
    typer.echo("")
    typer.echo(draft)


if __name__ == "__main__":
    app()
