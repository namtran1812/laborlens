from datetime import date

from laborlens.evaluation.backtest import (
    _build_episode_families,
    _percentile,
)
from laborlens.research.claims import (
    CandidateClaim,
)
from laborlens.research.episodes import (
    ClaimEpisode,
)


def episode(
    start_month: int,
    end_month: int,
    *,
    claim_type: str = "broad_contraction",
    score: float = -0.6,
) -> ClaimEpisode:
    claim = CandidateClaim(
        claim_id="test",
        observation_date=date(
            2024,
            start_month,
            1,
        ),
        claim_type=claim_type,
        headline="test",
        score=score,
        dispersion=0.2,
        coverage=1.0,
        confidence=0.8,
        evidence=(),
    )

    return ClaimEpisode(
        episode_id="test",
        claim_type=claim_type,
        start_date=date(
            2024,
            start_month,
            1,
        ),
        end_date=date(
            2024,
            end_month,
            1,
        ),
        representative=claim,
        duration_months=(end_month - start_month + 1),
        peak_confidence=0.8,
        claims=(claim,),
    )


def test_percentile_empty() -> None:
    assert (
        _percentile(
            [],
            0.9,
        )
        is None
    )


def test_percentile_single() -> None:
    assert (
        _percentile(
            [5.0],
            0.9,
        )
        == 5.0
    )


def test_percentile_interpolates() -> None:
    assert (
        _percentile(
            [
                1.0,
                2.0,
                3.0,
                4.0,
            ],
            0.5,
        )
        == 2.5
    )


def test_family_tracks_boundary_growth() -> None:
    families = _build_episode_families(
        [
            (
                date(2024, 7, 1),
                [
                    episode(
                        6,
                        6,
                    )
                ],
            ),
            (
                date(2024, 8, 1),
                [
                    episode(
                        6,
                        7,
                    )
                ],
            ),
        ],
        start_date=date(
            2024,
            1,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
    )

    assert len(families) == 1

    family = families[0]

    assert family.persistent_to_final
    assert family.start_drift_months == 0
    assert family.end_drift_months == 1


def test_family_detects_disappearance() -> None:
    families = _build_episode_families(
        [
            (
                date(2024, 7, 1),
                [
                    episode(
                        6,
                        6,
                    )
                ],
            ),
            (
                date(2024, 8, 1),
                [],
            ),
        ],
        start_date=date(
            2024,
            1,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
    )

    assert len(families) == 1

    assert not (families[0].persistent_to_final)


def test_family_tracks_type_flip() -> None:
    families = _build_episode_families(
        [
            (
                date(2024, 7, 1),
                [
                    episode(
                        6,
                        6,
                        claim_type=("broad_expansion"),
                        score=0.5,
                    )
                ],
            ),
            (
                date(2024, 8, 1),
                [
                    episode(
                        6,
                        6,
                        claim_type=("broad_contraction"),
                        score=-0.5,
                    )
                ],
            ),
        ],
        start_date=date(
            2024,
            1,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
    )

    assert len(families) == 1
    assert families[0].type_flipped
