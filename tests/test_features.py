from datetime import date

import pytest

from laborlens.analysis.features import (
    SeriesPoint,
    anomalies,
    compute_features,
)


def monthly_points(
    values: list[float],
) -> list[SeriesPoint]:
    return [
        SeriesPoint(
            observation_date=date(
                2024,
                index + 1,
                1,
            ),
            value=value,
        )
        for index, value in enumerate(values)
    ]


def test_delta_and_pct_change() -> None:
    points = monthly_points(
        [
            100.0,
            110.0,
            121.0,
            133.1,
        ]
    )

    result = compute_features(
        points,
        rolling_window=3,
    )

    assert result[1].delta_1 == 10.0

    assert result[1].pct_change_1 == pytest.approx(0.10)

    assert result[3].delta_3 == pytest.approx(33.1)

    assert result[3].pct_change_3 == pytest.approx(0.331)


def test_acceleration() -> None:
    points = monthly_points(
        [
            100.0,
            105.0,
            115.0,
        ]
    )

    result = compute_features(
        points,
        rolling_window=2,
    )

    assert result[2].delta_1 == 10.0

    assert result[2].acceleration == 5.0


def test_z_score_detects_outlier() -> None:
    points = monthly_points(
        [
            100.0,
            100.0,
            100.0,
            100.0,
            150.0,
        ]
    )

    result = compute_features(
        points,
        rolling_window=5,
    )

    assert result[-1].z_score == pytest.approx(2.0)

    flagged = anomalies(
        result,
        threshold=1.9,
    )

    assert len(flagged) == 1

    assert flagged[0].value == 150.0


def test_requires_valid_window() -> None:
    with pytest.raises(
        ValueError,
        match="rolling_window",
    ):
        compute_features(
            monthly_points([1.0]),
            rolling_window=1,
        )


def test_pct_change_handles_zero() -> None:
    points = monthly_points(
        [
            0.0,
            10.0,
        ]
    )

    result = compute_features(
        points,
        rolling_window=2,
    )

    assert result[1].pct_change_1 is None
