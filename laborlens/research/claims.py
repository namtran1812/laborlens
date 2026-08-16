from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from laborlens.analysis.regime import RegimePoint


@dataclass(frozen=True)
class EvidenceItem:
    series_id: str
    contribution: float


@dataclass(frozen=True)
class CandidateClaim:
    claim_id: str
    observation_date: date
    claim_type: str
    headline: str

    score: float
    dispersion: float
    coverage: float
    confidence: float

    evidence: tuple[EvidenceItem, ...]


def _confidence(
    point: RegimePoint,
) -> float:
    agreement = max(
        0.0,
        1.0 - point.dispersion / 2.5,
    )

    magnitude = min(
        1.0,
        abs(point.score),
    )

    confidence = 0.45 * point.coverage + 0.35 * agreement + 0.20 * magnitude

    return min(
        1.0,
        max(0.0, confidence),
    )


def _evidence(
    point: RegimePoint,
) -> tuple[EvidenceItem, ...]:
    ordered = sorted(
        point.smoothed_contributions.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return tuple(
        EvidenceItem(
            series_id=series_id,
            contribution=value,
        )
        for series_id, value in ordered
    )


def _directional_breadth(
    point: RegimePoint,
    direction: int,
) -> float:
    values = list(point.smoothed_contributions.values())

    if not values:
        return 0.0

    if direction < 0:
        aligned = sum(value < 0 for value in values)
    else:
        aligned = sum(value > 0 for value in values)

    return aligned / len(values)


def _has_material_disagreement(
    point: RegimePoint,
    *,
    minimum_magnitude: float = 0.20,
) -> bool:
    values = list(point.smoothed_contributions.values())

    positive = any(value >= minimum_magnitude for value in values)

    negative = any(value <= -minimum_magnitude for value in values)

    return positive and negative


def discover_claim(
    point: RegimePoint,
) -> CandidateClaim | None:
    if point.coverage < 0.8:
        return None

    evidence = _evidence(point)

    confidence = _confidence(point)

    date_id = point.observation_date.isoformat()

    if point.score <= -0.35 and point.dispersion <= 0.75 and _directional_breadth(point, -1) >= 0.8:
        return CandidateClaim(
            claim_id=(f"{date_id}-broad-weakness"),
            observation_date=(point.observation_date),
            claim_type=("broad_contraction"),
            headline=("Labor-market indicators are weakening broadly"),
            score=point.score,
            dispersion=point.dispersion,
            coverage=point.coverage,
            confidence=confidence,
            evidence=evidence,
        )

    if point.score >= 0.35 and point.dispersion <= 0.75 and _directional_breadth(point, 1) >= 0.8:
        return CandidateClaim(
            claim_id=(f"{date_id}-broad-strength"),
            observation_date=(point.observation_date),
            claim_type=("broad_expansion"),
            headline=("Labor-market indicators are strengthening broadly"),
            score=point.score,
            dispersion=point.dispersion,
            coverage=point.coverage,
            confidence=confidence,
            evidence=evidence,
        )

    if point.dispersion >= 1.0 and _has_material_disagreement(point):
        return CandidateClaim(
            claim_id=(f"{date_id}-divergence"),
            observation_date=(point.observation_date),
            claim_type=("signal_divergence"),
            headline=("Labor-market indicators are sending conflicting signals"),
            score=point.score,
            dispersion=point.dispersion,
            coverage=point.coverage,
            confidence=confidence,
            evidence=evidence,
        )

    return None


def discover_claims(
    points: list[RegimePoint],
    *,
    min_confidence: float = 0.55,
) -> list[CandidateClaim]:
    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("min_confidence must be between 0 and 1")

    claims = []

    for point in points:
        claim = discover_claim(point)

        if claim is not None and claim.confidence >= min_confidence:
            claims.append(claim)

    return claims
