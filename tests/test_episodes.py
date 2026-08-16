from datetime import date

from laborlens.research.claims import (
    CandidateClaim,
)
from laborlens.research.episodes import (
    cluster_claims,
)


def claim(
    month: int,
    *,
    claim_type: str = "broad_contraction",
    confidence: float = 0.8,
    score: float = -0.7,
) -> CandidateClaim:
    return CandidateClaim(
        claim_id=f"claim-{month}",
        observation_date=date(
            2024,
            month,
            1,
        ),
        claim_type=claim_type,
        headline="test",
        score=score,
        dispersion=0.4,
        coverage=1.0,
        confidence=confidence,
        evidence=(),
    )


def test_consecutive_claims_form_episode() -> None:
    episodes = cluster_claims(
        [
            claim(1),
            claim(2),
            claim(3),
        ]
    )

    assert len(episodes) == 1
    assert episodes[0].duration_months == 3
    assert episodes[0].start_date == date(
        2024,
        1,
        1,
    )
    assert episodes[0].end_date == date(
        2024,
        3,
        1,
    )


def test_gap_starts_new_episode() -> None:
    episodes = cluster_claims(
        [
            claim(1),
            claim(3),
        ]
    )

    assert len(episodes) == 2


def test_different_types_do_not_merge() -> None:
    episodes = cluster_claims(
        [
            claim(
                1,
                claim_type="broad_contraction",
            ),
            claim(
                2,
                claim_type="signal_divergence",
            ),
        ]
    )

    assert len(episodes) == 2


def test_highest_confidence_is_representative() -> None:
    episodes = cluster_claims(
        [
            claim(
                1,
                confidence=0.7,
            ),
            claim(
                2,
                confidence=0.95,
            ),
            claim(
                3,
                confidence=0.8,
            ),
        ]
    )

    assert episodes[0].representative.observation_date == date(2024, 2, 1)


def test_zero_gap_requires_same_month() -> None:
    episodes = cluster_claims(
        [
            claim(1),
            claim(2),
        ],
        max_gap_months=0,
    )

    assert len(episodes) == 2
