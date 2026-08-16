from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from laborlens.research.claims import CandidateClaim


@dataclass(frozen=True)
class ClaimEpisode:
    episode_id: str
    claim_type: str

    start_date: date
    end_date: date

    representative: CandidateClaim

    duration_months: int
    peak_confidence: float

    claims: tuple[CandidateClaim, ...]


def _month_distance(
    left: date,
    right: date,
) -> int:
    return (right.year - left.year) * 12 + right.month - left.month


def _representative(
    claims: list[CandidateClaim],
) -> CandidateClaim:
    return max(
        claims,
        key=lambda claim: (
            claim.confidence,
            abs(claim.score),
        ),
    )


def cluster_claims(
    claims: list[CandidateClaim],
    *,
    max_gap_months: int = 1,
) -> list[ClaimEpisode]:
    if max_gap_months < 0:
        raise ValueError("max_gap_months must be non-negative")

    ordered = sorted(
        claims,
        key=lambda claim: (
            claim.claim_type,
            claim.observation_date,
        ),
    )

    groups: list[list[CandidateClaim]] = []

    for claim in ordered:
        if not groups:
            groups.append([claim])
            continue

        current = groups[-1]
        previous = current[-1]

        same_type = claim.claim_type == previous.claim_type

        gap = _month_distance(
            previous.observation_date,
            claim.observation_date,
        )

        if same_type and gap <= max_gap_months:
            current.append(claim)
        else:
            groups.append([claim])

    episodes: list[ClaimEpisode] = []

    for group in groups:
        representative = _representative(group)

        start_date = group[0].observation_date
        end_date = group[-1].observation_date

        duration = (
            _month_distance(
                start_date,
                end_date,
            )
            + 1
        )

        episodes.append(
            ClaimEpisode(
                episode_id=(
                    f"{group[0].claim_type}-{start_date.isoformat()}-{end_date.isoformat()}"
                ),
                claim_type=(group[0].claim_type),
                start_date=start_date,
                end_date=end_date,
                representative=representative,
                duration_months=duration,
                peak_confidence=max(claim.confidence for claim in group),
                claims=tuple(group),
            )
        )

    return sorted(
        episodes,
        key=lambda episode: (
            episode.start_date,
            episode.claim_type,
        ),
    )
