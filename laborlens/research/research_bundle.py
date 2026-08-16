from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import fmean

from laborlens.analysis.regime import RegimePoint
from laborlens.research.claims import CandidateClaim
from laborlens.research.episodes import ClaimEpisode
from laborlens.research.evidence import EvidenceBundle
from laborlens.research.skeptic import SkepticVerdict


@dataclass(frozen=True)
class ProvenanceItem:
    series_id: str
    observation_date: date
    value: float
    realtime_start: date
    realtime_end: date


@dataclass(frozen=True)
class HistoricalAnalog:
    start_date: date
    end_date: date
    claim_type: str
    score: float
    confidence: float
    duration_months: int


@dataclass(frozen=True)
class ResearchBundle:
    episode_id: str
    claim: CandidateClaim
    episode: ClaimEpisode
    evidence: EvidenceBundle
    skeptic: SkepticVerdict

    duration_months: int
    mean_episode_score: float
    peak_episode_score: float

    historical_percentile: float
    comparable_observation_count: int
    historical_start_date: date | None
    historical_end_date: date | None
    historical_analogs: tuple[HistoricalAnalog, ...]

    provenance: tuple[ProvenanceItem, ...]


def historical_percentile(
    target_score: float,
    regimes: list[RegimePoint],
) -> float:
    comparable = [abs(point.score) for point in regimes if point.coverage >= 0.8]

    if not comparable:
        return 0.0

    target = abs(target_score)

    count = sum(value <= target for value in comparable)

    return count / len(comparable)


def find_historical_analogs(
    target: ClaimEpisode,
    episodes: list[ClaimEpisode],
    *,
    limit: int = 5,
) -> tuple[HistoricalAnalog, ...]:
    candidates = [
        episode
        for episode in episodes
        if (episode.episode_id != target.episode_id and episode.claim_type == target.claim_type)
    ]

    target_score = target.representative.score

    ranked = sorted(
        candidates,
        key=lambda episode: (
            abs(abs(episode.representative.score) - abs(target_score)),
            -episode.peak_confidence,
            -episode.duration_months,
        ),
    )

    return tuple(
        HistoricalAnalog(
            start_date=episode.start_date,
            end_date=episode.end_date,
            claim_type=episode.claim_type,
            score=episode.representative.score,
            confidence=episode.peak_confidence,
            duration_months=episode.duration_months,
        )
        for episode in ranked[:limit]
    )


def build_research_bundle(
    *,
    episode: ClaimEpisode,
    evidence: EvidenceBundle,
    skeptic: SkepticVerdict,
    regimes: list[RegimePoint],
    all_episodes: list[ClaimEpisode],
    provenance: list[ProvenanceItem],
) -> ResearchBundle:
    episode_regimes = [
        point
        for point in regimes
        if (episode.start_date <= point.observation_date <= episode.end_date)
    ]

    if episode_regimes:
        mean_score = fmean(point.score for point in episode_regimes)

        peak_score = max(
            (point.score for point in episode_regimes),
            key=abs,
        )
    else:
        mean_score = episode.representative.score

        peak_score = episode.representative.score

    comparable = [point for point in regimes if point.coverage >= 0.8]

    percentile = historical_percentile(
        episode.representative.score,
        comparable,
    )

    historical_start_date = comparable[0].observation_date if comparable else None

    historical_end_date = comparable[-1].observation_date if comparable else None

    analogs = find_historical_analogs(
        episode,
        all_episodes,
    )

    return ResearchBundle(
        episode_id=episode.episode_id,
        claim=episode.representative,
        episode=episode,
        evidence=evidence,
        skeptic=skeptic,
        duration_months=episode.duration_months,
        mean_episode_score=mean_score,
        peak_episode_score=peak_score,
        historical_percentile=percentile,
        comparable_observation_count=len(comparable),
        historical_start_date=historical_start_date,
        historical_end_date=historical_end_date,
        historical_analogs=analogs,
        provenance=tuple(provenance),
    )
