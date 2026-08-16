from __future__ import annotations

from dataclasses import dataclass

from laborlens.research.episodes import ClaimEpisode


@dataclass(frozen=True)
class EvidenceSignal:
    series_id: str
    contribution: float
    direction: str
    magnitude: float


@dataclass(frozen=True)
class EvidenceBundle:
    episode_id: str
    claim_type: str

    start_date: object
    end_date: object

    headline: str

    score: float
    dispersion: float
    coverage: float
    confidence: float

    supporting: tuple[EvidenceSignal, ...]
    opposing: tuple[EvidenceSignal, ...]

    breadth: float


def _direction(
    value: float,
) -> str:
    if value > 0:
        return "positive"

    if value < 0:
        return "negative"

    return "neutral"


def build_evidence_bundle(
    episode: ClaimEpisode,
    *,
    material_threshold: float = 0.20,
) -> EvidenceBundle:
    claim = episode.representative

    supporting = []
    opposing = []

    expected_direction = (
        -1
        if claim.claim_type == "broad_contraction"
        else 1
        if claim.claim_type == "broad_expansion"
        else 0
    )

    for item in claim.evidence:
        signal = EvidenceSignal(
            series_id=item.series_id,
            contribution=item.contribution,
            direction=_direction(item.contribution),
            magnitude=abs(item.contribution),
        )

        if expected_direction == 0:
            if abs(item.contribution) >= material_threshold:
                supporting.append(signal)
            continue

        aligned = item.contribution * expected_direction > 0

        material = abs(item.contribution) >= material_threshold

        if aligned and material:
            supporting.append(signal)

        elif material:
            opposing.append(signal)

    total_material = len(supporting) + len(opposing)

    breadth = len(supporting) / total_material if total_material else 0.0

    return EvidenceBundle(
        episode_id=episode.episode_id,
        claim_type=episode.claim_type,
        start_date=episode.start_date,
        end_date=episode.end_date,
        headline=claim.headline,
        score=claim.score,
        dispersion=claim.dispersion,
        coverage=claim.coverage,
        confidence=claim.confidence,
        supporting=tuple(supporting),
        opposing=tuple(opposing),
        breadth=breadth,
    )
