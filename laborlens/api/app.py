from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from laborlens.config import get_settings
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
