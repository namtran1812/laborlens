from datetime import date

import pytest

from laborlens.analysis.divergence import (
    AlignedPoint,
    align_series,
    compute_divergence,
    divergence_anomalies,
)


def test_align_series_uses_common_dates() -> None:
    left = [
        (
            date(2024, 1, 1),
            100.0,
        ),
        (
            date(2024, 2, 1),
            101.0,
        ),
    ]

    right = [
        (
            date(2024, 2, 1),
            4.0,
        ),
        (
            date(2024, 3, 1),
            4.1,
        ),
    ]

    result = align_series(
        left,
        right,
    )

    assert len(result) == 1

    assert result[0].observation_date == date(2024, 2, 1)

    assert result[0].left_value == 101.0
    assert result[0].right_value == 4.0


def test_divergence_detects_opposite_moves() -> None:
    values = [
        (100.0, 100.0),
        (101.0, 101.0),
        (102.0, 102.0),
        (103.0, 103.0),
        (104.0, 104.0),
        (105.0, 105.0),
        (90.0, 120.0),
    ]

    points = [
        AlignedPoint(
            observation_date=date(
                2024,
                index + 1,
                1,
            ),
            left_value=left,
            right_value=right,
        )
        for index, (
            left,
            right,
        ) in enumerate(values)
    ]

    result = compute_divergence(
        points,
        window=3,
    )

    last = result[-1]

    assert last.left_change_z is not None
    assert last.right_change_z is not None
    assert last.divergence is not None

    assert last.left_change_z < 0
    assert last.right_change_z > 0
    assert last.divergence < 0


def test_divergence_anomaly_threshold() -> None:
    values = [
        (100.0, 100.0),
        (101.0, 101.0),
        (102.0, 102.0),
        (103.0, 103.0),
        (104.0, 104.0),
        (105.0, 105.0),
        (80.0, 130.0),
    ]

    points = [
        AlignedPoint(
            observation_date=date(
                2024,
                index + 1,
                1,
            ),
            left_value=left,
            right_value=right,
        )
        for index, (
            left,
            right,
        ) in enumerate(values)
    ]

    result = compute_divergence(
        points,
        window=3,
    )

    flagged = divergence_anomalies(
        result,
        threshold=2.0,
    )

    assert flagged


def test_invalid_window() -> None:
    with pytest.raises(
        ValueError,
        match="window",
    ):
        compute_divergence(
            [],
            window=1,
        )
