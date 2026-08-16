from __future__ import annotations

import asyncio
from datetime import date

import typer

from laborlens.analysis.features import SeriesPoint, anomalies, compute_features
from laborlens.config import get_settings
from laborlens.data.fred import FredClient
from laborlens.data.qcew import QcewClient
from laborlens.services.ingestion import IngestionService
from laborlens.services.qcew_claim_pipeline import QcewClaimPipeline
from laborlens.services.qcew_ingestion import QcewIngestionService
from laborlens.services.qcew_research import QcewResearchService
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

    typer.echo(f"historical_comparisons={research.comparable_observation_count}")

    typer.echo(f"historical_range={research.historical_start_date}..{research.historical_end_date}")

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
    as_of: str | None = typer.Option(
        None,
        "--as-of",
        help=("Replay using only information available on YYYY-MM-DD."),
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
        start_date = date.fromisoformat(start)

        as_of_date = date.fromisoformat(as_of) if as_of is not None else None

    except ValueError as exc:
        raise typer.BadParameter("dates must use YYYY-MM-DD") from exc

    if as_of_date is not None and start_date > as_of_date:
        raise typer.BadParameter("--start cannot be later than --as-of")

    try:
        research = pipeline.build(
            start_date=start_date,
            window=window,
            min_confidence=min_confidence,
            as_of_date=as_of_date,
        )

    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if research.skeptic.verdict != "supported":
        typer.echo("Article generation blocked.")

        typer.echo(f"Reason: research episode verdict is {research.skeptic.verdict}.")

        raise typer.Exit(code=2)

    typer.echo(f"episode={research.episode_id}")

    typer.echo("mode=" + (f"as_of:{as_of_date}" if as_of_date is not None else "latest"))

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


@app.command("backfill-vintages")
def backfill_vintages(
    series_id: str,
    from_date: str = typer.Option(
        ...,
        "--from",
        help="Observation start date.",
    ),
    to_date: str = typer.Option(
        ...,
        "--to",
        help="Observation end date.",
    ),
    vintage_start: str = typer.Option(
        ...,
        "--vintage-start",
        help="Earliest FRED revision/release date.",
    ),
    vintage_end: str = typer.Option(
        ...,
        "--vintage-end",
        help="Latest FRED revision/release date.",
    ),
    batch_size: int = typer.Option(
        250,
        "--batch-size",
        help="Vintage dates fetched per observations request.",
    ),
) -> None:
    from laborlens.services.vintage_backfill import (
        VintageBackfillService,
    )

    if batch_size < 1:
        raise typer.BadParameter("--batch-size must be positive")

    try:
        observation_start = date.fromisoformat(from_date)

        observation_end = date.fromisoformat(to_date)

        resolved_vintage_start = date.fromisoformat(vintage_start)

        resolved_vintage_end = date.fromisoformat(vintage_end)

    except ValueError as exc:
        raise typer.BadParameter("dates must use YYYY-MM-DD") from exc

    if observation_start > observation_end:
        raise typer.BadParameter("--from cannot be later than --to")

    if resolved_vintage_start > resolved_vintage_end:
        raise typer.BadParameter("--vintage-start cannot be later than --vintage-end")

    settings = get_settings()

    service = VintageBackfillService(
        FredClient(settings.fred_api_key),
        ClickHouseStore(settings),
    )

    vintage_count, inserted = asyncio.run(
        service.backfill_release_dates(
            series_id,
            vintage_start=(resolved_vintage_start),
            vintage_end=(resolved_vintage_end),
            observation_start=(observation_start),
            observation_end=(observation_end),
            batch_size=batch_size,
        )
    )

    typer.echo(f"series={series_id.upper()}")

    typer.echo(f"release_vintages={vintage_count}")

    typer.echo(f"inserted={inserted}")


@app.command("replay-eval")
def replay_eval(
    from_date: str = typer.Option(
        ...,
        "--from",
        help="First historical information date.",
    ),
    to_date: str = typer.Option(
        ...,
        "--to",
        help="Final historical information date.",
    ),
    target: str = typer.Option(
        ...,
        "--target",
        help=("Observation month identifying the episode to track."),
    ),
    schedule: str = typer.Option(
        "releases",
        "--schedule",
        help="Replay schedule: releases or fixed.",
    ),
    step_days: int = typer.Option(
        30,
        "--step-days",
        help=("Days between states when --schedule fixed is used."),
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
    )
    from laborlens.evaluation.replay import (
        evaluate_replay,
    )
    from laborlens.services.research_pipeline import (
        ResearchPipeline,
    )

    try:
        start_date = date.fromisoformat(from_date)
        end_date = date.fromisoformat(to_date)
        target_date = date.fromisoformat(target)

    except ValueError as exc:
        raise typer.BadParameter("dates must use YYYY-MM-DD") from exc

    if start_date > end_date:
        raise typer.BadParameter("--from cannot be later than --to")

    if target_date > end_date:
        raise typer.BadParameter("--target cannot be later than --to")

    if step_days < 1:
        raise typer.BadParameter("--step-days must be positive")

    if schedule not in {
        "releases",
        "fixed",
    }:
        raise typer.BadParameter("--schedule must be releases or fixed")

    settings = get_settings()

    store = ClickHouseStore(settings)

    evaluation_dates = None

    if schedule == "releases":
        evaluation_dates = store.information_dates(
            list(DEFAULT_SPECS.keys()),
            start_date,
            end_date,
        )

        if not evaluation_dates:
            raise typer.BadParameter(
                "no release information dates were found in the requested range"
            )

    result = evaluate_replay(
        ResearchPipeline(store),
        start_date=start_date,
        end_date=end_date,
        target_date=target_date,
        step_days=step_days,
        window=window,
        min_confidence=min_confidence,
        evaluation_dates=evaluation_dates,
    )

    typer.echo(f"target={target_date}")
    typer.echo(f"schedule={schedule}")
    typer.echo(f"replay_dates={result.replay_dates}")
    typer.echo(f"detected_states={result.detected_states}")
    typer.echo(f"missing_states={result.missing_states}")
    typer.echo("")

    for state in result.tracked:
        episode = state.episode

        if episode is None:
            typer.echo(f"{state.as_of_date}\tepisode=not_detected")
            continue

        typer.echo(
            f"{state.as_of_date}\t"
            f"period={episode.start_date}"
            f"..{episode.end_date}\t"
            f"type={episode.claim_type}\t"
            f"score="
            f"{episode.representative.score:.3f}\t"
            f"confidence="
            f"{episode.peak_confidence:.3f}"
        )

    typer.echo("")
    typer.echo("revision_metrics:")

    typer.echo(f"  first_detected_as_of={result.first_detected_as_of}")

    typer.echo(f"  previous_information_state={result.previous_information_state}")

    detection_series = []

    if result.first_detected_as_of is not None:
        detection_series = store.information_series_on_date(
            list(DEFAULT_SPECS.keys()),
            result.first_detected_as_of,
        )

    typer.echo(
        "  detection_release_series=" + (",".join(detection_series) if detection_series else "none")
    )

    typer.echo(f"  last_detected_as_of={result.last_detected_as_of}")

    typer.echo(f"  detection_latency_days={result.detection_latency_days}")

    if result.survival_rate is None:
        typer.echo("  survival_rate=n/a")
    else:
        typer.echo(f"  survival_rate={result.survival_rate:.1%}")

    typer.echo(f"  claim_type_flips={result.claim_type_flips}")

    typer.echo(f"  initial_score={result.initial_score}")

    typer.echo(f"  final_score={result.final_score}")

    typer.echo(f"  absolute_score_revision={result.absolute_score_revision}")

    typer.echo(f"  initial_confidence={result.initial_confidence}")

    typer.echo(f"  final_confidence={result.final_confidence}")

    typer.echo(f"  mean_score_drift={result.mean_score_drift}")

    typer.echo(f"  max_score_drift={result.max_score_drift}")

    typer.echo(f"  start_drift_months={result.start_drift_months}")

    typer.echo(f"  end_drift_months={result.end_drift_months}")


@app.command("backtest")
def backtest(
    from_date: str = typer.Option(
        ...,
        "--from",
        help="Beginning of evaluation range.",
    ),
    to_date: str = typer.Option(
        ...,
        "--to",
        help="Final information state.",
    ),
    window: int = typer.Option(
        24,
        "--window",
    ),
    min_confidence: float = typer.Option(
        0.55,
        "--min-confidence",
    ),
    show_episodes: bool = typer.Option(
        False,
        "--show-episodes",
    ),
    show_families: bool = typer.Option(
        False,
        "--show-families",
    ),
) -> None:
    from laborlens.evaluation.backtest import (
        run_backtest,
    )
    from laborlens.services.research_pipeline import (
        ResearchPipeline,
    )

    try:
        start_date = date.fromisoformat(from_date)
        end_date = date.fromisoformat(to_date)

    except ValueError as exc:
        raise typer.BadParameter("dates must use YYYY-MM-DD") from exc

    if start_date > end_date:
        raise typer.BadParameter("--from cannot be later than --to")

    settings = get_settings()

    store = ClickHouseStore(settings)

    try:
        result = run_backtest(
            store,
            ResearchPipeline(store),
            start_date=start_date,
            end_date=end_date,
            window=window,
            min_confidence=min_confidence,
        )

    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if show_episodes:
        typer.echo("final_state_episodes:")

        for item in result.episodes:
            replay = item.replay

            typer.echo(
                f"{item.target_date}\t"
                f"type={item.claim_type}\t"
                f"final_period="
                f"{item.final_start_date}"
                f"..{item.final_end_date}\t"
                f"first_detected="
                f"{replay.first_detected_as_of}\t"
                f"latency="
                f"{replay.detection_latency_days}\t"
                f"survival="
                + (f"{replay.survival_rate:.1%}" if replay.survival_rate is not None else "n/a")
                + "\t"
                f"score_revision="
                f"{replay.absolute_score_revision}"
            )

        typer.echo("")

    if show_families:
        typer.echo("realtime_episode_families:")

        for family in result.families:
            typer.echo(
                f"family={family.family_id}\t"
                f"first_seen="
                f"{family.first_seen_as_of}\t"
                f"last_seen="
                f"{family.last_seen_as_of}\t"
                f"first_period="
                f"{family.first_episode.start_date}"
                f"..{family.first_episode.end_date}\t"
                f"final_period="
                f"{family.final_episode.start_date}"
                f"..{family.final_episode.end_date}\t"
                f"type="
                f"{family.first_episode.claim_type}"
                f"->{family.final_episode.claim_type}\t"
                f"persistent="
                f"{family.persistent_to_final}\t"
                f"type_flipped="
                f"{family.type_flipped}\t"
                f"observations="
                f"{family.observations}"
            )

        typer.echo("")

    typer.echo("final_state_backtest:")

    typer.echo(f"  episodes_evaluated={result.episodes_evaluated}")

    typer.echo(f"  episodes_detected={result.episodes_detected}")

    typer.echo(f"  episodes_never_detected={result.episodes_never_detected}")

    if result.detection_rate is None:
        typer.echo("  detection_rate=n/a")
    else:
        typer.echo(f"  detection_rate={result.detection_rate:.1%}")

    typer.echo(f"  median_detection_latency_days={result.median_detection_latency_days}")

    typer.echo(f"  p90_detection_latency_days={result.p90_detection_latency_days}")

    if result.mean_survival_rate is None:
        typer.echo("  mean_survival_rate=n/a")
    else:
        typer.echo(f"  mean_survival_rate={result.mean_survival_rate:.1%}")

    if result.claim_type_flip_rate is None:
        typer.echo("  claim_type_flip_rate=n/a")
    else:
        typer.echo(f"  claim_type_flip_rate={result.claim_type_flip_rate:.1%}")

    typer.echo(f"  median_absolute_score_revision={result.median_absolute_score_revision}")

    typer.echo(f"  p90_absolute_score_revision={result.p90_absolute_score_revision}")

    typer.echo(f"  mean_start_drift_months={result.mean_start_drift_months}")

    typer.echo(f"  mean_end_drift_months={result.mean_end_drift_months}")

    typer.echo("")

    typer.echo("anti_survivorship:")

    typer.echo(f"  realtime_episode_families={result.realtime_episode_families}")

    typer.echo(f"  persistent_families={result.persistent_families}")

    typer.echo(f"  disappeared_families={result.disappeared_families}")

    typer.echo(f"  final_only_families={result.final_only_families}")

    if result.persistence_rate is None:
        typer.echo("  persistence_rate=n/a")
    else:
        typer.echo(f"  persistence_rate={result.persistence_rate:.1%}")

    if result.revision_disappearance_rate is None:
        typer.echo("  revision_disappearance_rate=n/a")
    else:
        typer.echo(f"  revision_disappearance_rate={result.revision_disappearance_rate:.1%}")

    typer.echo(f"  type_flipped_families={result.type_flipped_families}")

    if result.type_flip_family_rate is None:
        typer.echo("  type_flip_family_rate=n/a")
    else:
        typer.echo(f"  type_flip_family_rate={result.type_flip_family_rate:.1%}")

    typer.echo(f"  mean_family_start_drift_months={result.mean_family_start_drift_months}")

    typer.echo(f"  mean_family_end_drift_months={result.mean_family_end_drift_months}")


@app.command("ingest-qcew")
def ingest_qcew(
    year: int = typer.Option(
        ...,
        "--year",
        min=1975,
        help="QCEW publication year.",
    ),
    quarter: int = typer.Option(
        ...,
        "--quarter",
        min=1,
        max=4,
        help="QCEW quarter.",
    ),
    batch_size: int = typer.Option(
        25_000,
        "--batch-size",
        min=1_000,
        max=250_000,
        help="ClickHouse insert batch size.",
    ),
) -> None:
    """Download and ingest one real BLS QCEW quarterly publication."""

    settings = get_settings()

    store = ClickHouseStore(settings)

    service = QcewIngestionService(
        QcewClient(),
        store,
    )

    result = asyncio.run(
        service.ingest_quarter(
            year,
            quarter,
            batch_size=batch_size,
        )
    )

    typer.echo(f"year={result.year}")

    typer.echo(f"quarter={result.quarter}")

    typer.echo(f"rows_received={result.rows_received}")

    typer.echo(f"rows_valid={result.rows_valid}")

    typer.echo(f"rows_inserted={result.rows_inserted}")


@app.command("compare-qcew")
def compare_qcew(
    area_fips: str = typer.Option(
        ...,
        "--area",
        help="QCEW area FIPS code.",
    ),
    year: int = typer.Option(
        ...,
        "--year",
    ),
    quarter: int = typer.Option(
        ...,
        "--quarter",
        min=1,
        max=4,
    ),
    minimum_employment: int = typer.Option(
        10_000,
        "--minimum-employment",
        min=0,
    ),
    industry_level: int = typer.Option(
        6,
        "--industry-level",
        min=2,
        max=6,
        help="NAICS industry depth.",
    ),
    limit: int = typer.Option(
        25,
        "--limit",
        min=1,
        max=500,
    ),
) -> None:
    """Compare local industries against national QCEW growth."""

    settings = get_settings()

    service = QcewResearchService(ClickHouseStore(settings))

    results = service.compare_area_to_national(
        area_fips=area_fips,
        year=year,
        quarter=quarter,
        minimum_employment=minimum_employment,
        industry_level=industry_level,
    )

    typer.echo("industry\tlocal_emp\tlocal_yoy\tnational_yoy\trelative\tlq\tweakening")

    for result in results[:limit]:
        local_yoy = (
            f"{result.local_yoy_growth:.1f}" if result.local_yoy_growth is not None else "n/a"
        )
        national_yoy = (
            f"{result.national_yoy_growth:.1f}" if result.national_yoy_growth is not None else "n/a"
        )
        relative = f"{result.relative_growth:.1f}" if result.relative_growth is not None else "n/a"
        lq = (
            f"{result.local_location_quotient:.2f}"
            if result.local_location_quotient is not None
            else "n/a"
        )
        score = f"{result.weakening_score:.2f}" if result.weakening_score is not None else "n/a"

        typer.echo(
            f"{result.industry_code}\t"
            f"{result.comparison_type}\t"
            f"{result.industry_title}\t"
            f"{result.local_employment}\t"
            f"{local_yoy}\t"
            f"{national_yoy}\t"
            f"{relative}\t"
            f"{lq}\t"
            f"{score}"
        )


@app.command("qcew-claims")
def qcew_claims(
    area_fips: str = typer.Option(
        ...,
        "--area",
    ),
    year: int = typer.Option(
        ...,
        "--year",
    ),
    quarter: int = typer.Option(
        ...,
        "--quarter",
        min=1,
        max=4,
    ),
    industry_level: int = typer.Option(
        6,
        "--industry-level",
        min=2,
        max=6,
    ),
    minimum_employment: int = typer.Option(
        10_000,
        "--minimum-employment",
        min=0,
    ),
    minimum_relative_gap: float = typer.Option(
        2.0,
        "--minimum-relative-gap",
        min=0.0,
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        min=1,
        max=100,
    ),
) -> None:
    """Discover validated cross-sectional QCEW claims."""

    pipeline = QcewClaimPipeline(ClickHouseStore(get_settings()))

    results = pipeline.discover(
        area_fips=area_fips,
        year=year,
        quarter=quarter,
        industry_level=industry_level,
        minimum_employment=minimum_employment,
        minimum_relative_gap=minimum_relative_gap,
        limit=limit,
    )

    typer.echo(f"validated_claims={len(results)}")
    typer.echo("")

    for result in results:
        claim = result.claim

        typer.echo(
            f"{claim.claim_type}\t"
            f"{claim.industry_code}\t"
            f"skeptic={result.skeptic.verdict}\t"
            f"strength={claim.strength:.2f}"
        )

        typer.echo(f"  {claim.headline}")

        typer.echo(f"  {claim.evidence_text}")

        if claim.location_quotient is not None:
            typer.echo(f"  location_quotient={claim.location_quotient:.2f}")

        typer.echo("")


if __name__ == "__main__":
    app()
