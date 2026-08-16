from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from laborlens.analysis.regime import DEFAULT_SPECS
from laborlens.config import get_settings
from laborlens.evaluation.replay import evaluate_replay
from laborlens.services.research_pipeline import ResearchPipeline
from laborlens.storage.clickhouse import ClickHouseStore
from laborlens.writer.deterministic_writer import write_deterministic_article

app = FastAPI(
    title="LaborLens API",
    description=("Revision-aware labor-market research API built on FRED/ALFRED vintages."),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def pipeline() -> ResearchPipeline:
    store = ClickHouseStore(get_settings())
    return ResearchPipeline(store)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "laborlens",
    }


@app.get("/episodes")
def episodes(
    window: int = Query(
        24,
        ge=6,
        le=60,
    ),
    min_confidence: float = Query(
        0.55,
        ge=0.0,
        le=1.0,
    ),
    as_of: Annotated[
        date | None,
        Query(),
    ] = None,
) -> dict:
    result = pipeline().discover_episodes(
        window=window,
        min_confidence=min_confidence,
        as_of_date=as_of,
    )

    return {
        "count": len(result),
        "episodes": [
            {
                "episode_id": episode.episode_id,
                "claim_type": episode.claim_type,
                "start_date": episode.start_date,
                "end_date": episode.end_date,
                "duration_months": episode.duration_months,
                "peak_confidence": episode.peak_confidence,
                "score": (episode.representative.score),
                "headline": (episode.representative.headline),
            }
            for episode in result
        ],
    }


@app.get("/episodes/{start_date}")
def episode_detail(
    start_date: date,
    window: int = Query(
        24,
        ge=6,
        le=60,
    ),
    min_confidence: float = Query(
        0.55,
        ge=0.0,
        le=1.0,
    ),
    as_of: Annotated[
        date | None,
        Query(),
    ] = None,
) -> dict:
    try:
        bundle = pipeline().build(
            start_date=start_date,
            window=window,
            min_confidence=min_confidence,
            as_of_date=as_of,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    episode = bundle.episode

    return {
        "episode": {
            "episode_id": (episode.episode_id),
            "claim_type": (episode.claim_type),
            "start_date": (episode.start_date),
            "end_date": (episode.end_date),
            "duration_months": (episode.duration_months),
            "peak_confidence": (episode.peak_confidence),
            "score": (episode.representative.score),
            "headline": (episode.representative.headline),
        },
        "skeptic": {
            "verdict": (bundle.skeptic.verdict),
            "score": (bundle.skeptic.score),
        },
        "evidence": {
            "supporting": [
                {
                    "series_id": (item.series_id),
                    "contribution": (item.contribution),
                }
                for item in bundle.evidence.supporting
            ],
            "counter": [
                {
                    "series_id": (item.series_id),
                    "contribution": (item.contribution),
                }
                for item in bundle.evidence.opposing
            ],
        },
        "historical_percentile": (bundle.historical_percentile),
        "mean_episode_score": (bundle.mean_episode_score),
        "peak_episode_score": (bundle.peak_episode_score),
        "provenance_rows": len(bundle.provenance),
    }


@app.get("/article/{start_date}")
def article(
    start_date: date,
    window: int = Query(
        24,
        ge=6,
        le=60,
    ),
    min_confidence: float = Query(
        0.55,
        ge=0.0,
        le=1.0,
    ),
    as_of: Annotated[
        date | None,
        Query(),
    ] = None,
) -> dict:
    try:
        bundle = pipeline().build(
            start_date=start_date,
            window=window,
            min_confidence=min_confidence,
            as_of_date=as_of,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "episode_id": (bundle.episode.episode_id),
        "article": (write_deterministic_article(bundle)),
    }


@app.get("/replay")
def replay(
    from_date: Annotated[
        date,
        Query(alias="from"),
    ],
    to_date: Annotated[
        date,
        Query(alias="to"),
    ],
    target: Annotated[
        date,
        Query(),
    ],
    schedule: Annotated[
        str,
        Query(pattern="^(releases|fixed)$"),
    ] = "releases",
    step_days: Annotated[
        int,
        Query(ge=1, le=365),
    ] = 30,
    window: Annotated[
        int,
        Query(ge=6, le=60),
    ] = 24,
    min_confidence: Annotated[
        float,
        Query(ge=0.0, le=1.0),
    ] = 0.55,
) -> dict:
    if from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail=("'from' cannot be later than 'to'"),
        )

    store = ClickHouseStore(get_settings())

    research_pipeline = ResearchPipeline(store)

    evaluation_dates = None

    if schedule == "releases":
        evaluation_dates = store.information_dates(
            list(DEFAULT_SPECS.keys()),
            from_date,
            to_date,
        )

        if not evaluation_dates:
            raise HTTPException(
                status_code=404,
                detail=("No release information dates found in range"),
            )

    try:
        result = evaluate_replay(
            research_pipeline,
            start_date=from_date,
            end_date=to_date,
            target_date=target,
            step_days=step_days,
            window=window,
            min_confidence=min_confidence,
            evaluation_dates=evaluation_dates,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    release_series = []

    if schedule == "releases" and result.first_detected_as_of is not None:
        release_series = store.information_series_on_date(
            list(DEFAULT_SPECS.keys()),
            result.first_detected_as_of,
        )

    reference = result.reference_episode

    return {
        "target": target,
        "schedule": schedule,
        "from_date": from_date,
        "to_date": to_date,
        "reference_episode": (
            {
                "episode_id": (reference.episode_id),
                "claim_type": (reference.claim_type),
                "start_date": (reference.start_date),
                "end_date": (reference.end_date),
                "headline": (reference.representative.headline),
                "score": (reference.representative.score),
                "confidence": (reference.peak_confidence),
            }
            if reference is not None
            else None
        ),
        "states": [
            {
                "as_of_date": (state.as_of_date),
                "detected": (state.episode is not None),
                "episode": (
                    {
                        "episode_id": (state.episode.episode_id),
                        "claim_type": (state.episode.claim_type),
                        "start_date": (state.episode.start_date),
                        "end_date": (state.episode.end_date),
                        "score": (state.episode.representative.score),
                        "confidence": (state.episode.peak_confidence),
                    }
                    if state.episode is not None
                    else None
                ),
            }
            for state in result.tracked
        ],
        "metrics": {
            "replay_dates": (result.replay_dates),
            "detected_states": (result.detected_states),
            "missing_states": (result.missing_states),
            "first_detected_as_of": (result.first_detected_as_of),
            "previous_information_state": (result.previous_information_state),
            "last_detected_as_of": (result.last_detected_as_of),
            "detection_release_series": (release_series),
            "detection_latency_days": (result.detection_latency_days),
            "survival_rate": (result.survival_rate),
            "claim_type_flips": (result.claim_type_flips),
            "initial_score": (result.initial_score),
            "final_score": (result.final_score),
            "absolute_score_revision": (result.absolute_score_revision),
            "initial_confidence": (result.initial_confidence),
            "final_confidence": (result.final_confidence),
            "mean_score_drift": (result.mean_score_drift),
            "max_score_drift": (result.max_score_drift),
            "start_drift_months": (result.start_drift_months),
            "end_drift_months": (result.end_drift_months),
        },
    }
