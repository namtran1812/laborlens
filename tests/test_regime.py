from datetime import date

import pytest

from laborlens.analysis.regime import (
    DEFAULT_SPECS,
    SignalValue,
    compute_regime,
    compute_signal,
    monthly_average,
)


def test_monthly_average() -> None:
    points = [
        (
            date(2024, 1, 6),
            200.0,
        ),
        (
            date(2024, 1, 13),
            220.0,
        ),
        (
            date(2024, 2, 3),
            240.0,
        ),
    ]

    result = monthly_average(points)

    assert result == [
        (
            date(2024, 1, 1),
            210.0,
        ),
        (
            date(2024, 2, 1),
            240.0,
        ),
    ]


def test_unrate_uses_level_difference() -> None:
    spec = DEFAULT_SPECS["UNRATE"]

    points = [
        (
            date(2024, 1, 1),
            4.0,
        ),
        (
            date(2024, 2, 1),
            4.2,
        ),
        (
            date(2024, 3, 1),
            4.3,
        ),
    ]

    result = compute_signal(
        points,
        spec,
        window=2,
    )

    assert result[1].change == pytest.approx(0.2)

    assert result[2].change == pytest.approx(0.1)


def test_unemployment_direction_is_inverted() -> None:
    spec = DEFAULT_SPECS["UNRATE"]

    points = [
        (
            date(2024, 1, 1),
            4.0,
        ),
        (
            date(2024, 2, 1),
            4.0,
        ),
        (
            date(2024, 3, 1),
            5.0,
        ),
    ]

    result = compute_signal(
        points,
        spec,
        window=2,
    )

    assert result[-1].contribution is not None

    assert result[-1].contribution < 0


def test_regime_averages_contributions() -> None:
    d = date(
        2024,
        1,
        1,
    )

    def signal(
        contribution: float,
    ) -> SignalValue:
        return SignalValue(
            observation_date=d,
            raw_value=1.0,
            change=0.1,
            z_score=contribution,
            contribution=contribution,
        )

    signals = {
        "A": [signal(-1.0)],
        "B": [signal(-2.0)],
        "C": [signal(-1.5)],
    }

    result = compute_regime(signals)

    assert len(result) == 1

    assert result[0].raw_score == -1.5
    assert result[0].score == -1.5

    assert result[0].label == "strong_contraction"


def test_regime_smoothing_reduces_one_month_flip() -> None:
    dates = [
        date(2024, 1, 1),
        date(2024, 2, 1),
        date(2024, 3, 1),
    ]

    def values(
        contributions: list[float],
    ) -> list[SignalValue]:
        return [
            SignalValue(
                observation_date=d,
                raw_value=1.0,
                change=0.1,
                z_score=value,
                contribution=value,
            )
            for d, value in zip(
                dates,
                contributions,
                strict=True,
            )
        ]

    signals = {
        "A": values(
            [
                1.5,
                -1.5,
                1.5,
            ]
        ),
        "B": values(
            [
                1.5,
                -1.5,
                1.5,
            ]
        ),
        "C": values(
            [
                1.5,
                -1.5,
                1.5,
            ]
        ),
    }

    result = compute_regime(
        signals,
        smoothing_window=3,
    )

    assert result[-1].raw_score == 1.5
    assert result[-1].score == 0.5
    assert result[-1].label == "expansion"


def test_low_coverage_is_explicit() -> None:
    d = date(
        2024,
        1,
        1,
    )

    def signal(
        value: float | None,
    ) -> list[SignalValue]:
        return [
            SignalValue(
                observation_date=d,
                raw_value=1.0,
                change=0.1,
                z_score=value,
                contribution=value,
            )
        ]

    signals = {
        "A": signal(1.0),
        "B": signal(1.0),
        "C": signal(1.0),
        "D": signal(None),
        "E": signal(None),
    }

    result = compute_regime(
        signals,
        min_signals=3,
    )

    assert len(result) == 1
    assert result[0].coverage == 0.6
    assert result[0].label == "low_coverage"
