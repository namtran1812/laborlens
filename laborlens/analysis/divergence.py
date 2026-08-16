from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from statistics import fmean


@dataclass(frozen=True)
class AlignedPoint:
    observation_date: date
    left_value: float
    right_value: float


@dataclass(frozen=True)
class DivergencePoint:
    observation_date: date

    left_value: float
    right_value: float

    left_change: float | None
    right_change: float | None

    left_change_z: float | None
    right_change_z: float | None

    divergence: float | None
    correlation: float | None


def align_series(
    left: list[tuple[date, float]],
    right: list[tuple[date, float]],
) -> list[AlignedPoint]:
    left_map = {observation_date: value for observation_date, value in left}

    right_map = {observation_date: value for observation_date, value in right}

    common_dates = sorted(set(left_map) & set(right_map))

    return [
        AlignedPoint(
            observation_date=observation_date,
            left_value=left_map[observation_date],
            right_value=right_map[observation_date],
        )
        for observation_date in common_dates
    ]


def _pct_change(
    current: float,
    previous: float,
) -> float | None:
    if previous == 0:
        return None

    return (current - previous) / abs(previous)


def _mean_std(
    values: list[float],
) -> tuple[float, float]:
    mean = fmean(values)

    variance = fmean((value - mean) ** 2 for value in values)

    return mean, sqrt(variance)


def _z_score(
    values: list[float],
    current: float,
) -> float:
    mean, std = _mean_std(values)

    if std == 0:
        return 0.0

    return (current - mean) / std


def _correlation(
    left: list[float],
    right: list[float],
) -> float | None:
    if len(left) != len(right):
        raise ValueError("correlation inputs must have equal length")

    if len(left) < 2:
        return None

    left_mean = fmean(left)
    right_mean = fmean(right)

    numerator = sum(
        (x - left_mean) * (y - right_mean)
        for x, y in zip(
            left,
            right,
            strict=True,
        )
    )

    left_ss = sum((x - left_mean) ** 2 for x in left)

    right_ss = sum((y - right_mean) ** 2 for y in right)

    denominator = sqrt(left_ss * right_ss)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def compute_divergence(
    points: list[AlignedPoint],
    *,
    window: int = 12,
) -> list[DivergencePoint]:
    if window < 2:
        raise ValueError("window must be at least 2")

    ordered = sorted(
        points,
        key=lambda point: point.observation_date,
    )

    left_changes: list[float | None] = []
    right_changes: list[float | None] = []

    for index, point in enumerate(ordered):
        if index == 0:
            left_changes.append(None)
            right_changes.append(None)
            continue

        previous = ordered[index - 1]

        left_changes.append(
            _pct_change(
                point.left_value,
                previous.left_value,
            )
        )

        right_changes.append(
            _pct_change(
                point.right_value,
                previous.right_value,
            )
        )

    result: list[DivergencePoint] = []

    for index, point in enumerate(ordered):
        left_change = left_changes[index]
        right_change = right_changes[index]

        left_z = None
        right_z = None
        divergence = None
        correlation = None

        start = index - window + 1

        if start >= 1 and left_change is not None and right_change is not None:
            window_left = [value for value in left_changes[start : index + 1] if value is not None]

            window_right = [
                value for value in right_changes[start : index + 1] if value is not None
            ]

            if len(window_left) == window and len(window_right) == window:
                left_z = _z_score(
                    window_left,
                    left_change,
                )

                right_z = _z_score(
                    window_right,
                    right_change,
                )

                divergence = left_z - right_z

                if abs(divergence) < 1e-12:
                    divergence = 0.0

                correlation = _correlation(
                    window_left,
                    window_right,
                )

        result.append(
            DivergencePoint(
                observation_date=(point.observation_date),
                left_value=point.left_value,
                right_value=point.right_value,
                left_change=left_change,
                right_change=right_change,
                left_change_z=left_z,
                right_change_z=right_z,
                divergence=divergence,
                correlation=correlation,
            )
        )

    return result


def divergence_anomalies(
    points: list[DivergencePoint],
    *,
    threshold: float = 2.0,
) -> list[DivergencePoint]:
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    return [
        point
        for point in points
        if (point.divergence is not None and abs(point.divergence) >= threshold)
    ]
