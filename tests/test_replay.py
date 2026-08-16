from datetime import date
from unittest.mock import Mock

import pytest

from laborlens.evaluation.replay import (
    evaluate_replay,
    replay_dates,
)
from laborlens.research.claims import CandidateClaim
from laborlens.research.episodes import ClaimEpisode


def episode(
    start_month: int,
    end_month: int,
    *,
    claim_type: str = "broad_contraction",
    score: float = -0.6,
    confidence: float = 0.8,
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
        confidence=confidence,
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
        peak_confidence=confidence,
        claims=(claim,),
    )


def test_replay_dates_includes_end() -> None:
    result = replay_dates(
        date(2024, 1, 1),
        date(2024, 3, 1),
        step_days=30,
    )

    assert result[-1] == date(
        2024,
        3,
        1,
    )


def test_tracks_overlapping_episode() -> None:
    pipeline = Mock()

    pipeline.discover_episodes.side_effect = [
        [],
        [
            episode(
                6,
                6,
                score=-0.5,
            )
        ],
        [
            episode(
                6,
                8,
                score=-0.7,
            )
        ],
    ]

    result = evaluate_replay(
        pipeline,
        start_date=date(
            2024,
            6,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
        target_date=date(
            2024,
            6,
            1,
        ),
        step_days=31,
    )

    assert result.detected_states == 2

    assert result.first_detected_as_of == date(
        2024,
        7,
        2,
    )

    assert result.final_score == -0.7

    assert result.absolute_score_revision == pytest.approx(0.2)


def test_tracks_type_flip_by_overlap() -> None:
    pipeline = Mock()

    pipeline.discover_episodes.side_effect = [
        [
            episode(
                6,
                6,
                claim_type="broad_expansion",
                score=0.4,
            )
        ],
        [
            episode(
                6,
                6,
                claim_type="broad_contraction",
                score=-0.5,
            )
        ],
    ]

    result = evaluate_replay(
        pipeline,
        start_date=date(
            2024,
            7,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
        target_date=date(
            2024,
            6,
            1,
        ),
        step_days=31,
    )

    assert result.claim_type_flips == 1
