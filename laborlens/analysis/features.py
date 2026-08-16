from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from statistics import fmean


@dataclass(frozen=True)
class SeriesPoint:
    observation_date: date
    value: float


@dataclass(frozen=True)
class FeaturePoint:
    observation_date: date
    value: float

    delta_1: float | None
    delta_3: float | None

    pct_change_1: float | None
    pct_change_3: float | None
    pct_change_12: float | None

    rolling_mean: float | None
    rolling_std: float | None
    z_score: float | None

    acceleration: float | None
    anomaly_score: float | None


def _delta(
    points: list[SeriesPoint],
    index: int,
    periods: int,
) -> float | None:
    previous_index = index - periods

    if previous_index < 0:
        return None

    return points[index].value - points[previous_index].value


def _pct_change(
    points: list[SeriesPoint],
    index: int,
    periods: int,
) -> float | None:
    previous_index = index - periods

    if previous_index < 0:
        return None

    previous = points[previous_index].value

    if previous == 0:
        return None

    return (points[index].value - previous) / abs(previous)


def _rolling_statistics(
    points: list[SeriesPoint],
    index: int,
    window: int,
) -> tuple[
    float | None,
    float | None,
    float | None,
]:
    start = index - window + 1

    if start < 0:
        return None, None, None

    values = [point.value for point in points[start : index + 1]]

    mean = fmean(values)

    variance = fmean([(value - mean) ** 2 for value in values])

    std = sqrt(variance)

    if std == 0:
        z_score = 0.0
    else:
        z_score = (points[index].value - mean) / std

    return mean, std, z_score


def compute_features(
    points: list[SeriesPoint],
    *,
    rolling_window: int = 12,
) -> list[FeaturePoint]:
    if rolling_window < 2:
        raise ValueError("rolling_window must be at least 2")

    ordered = sorted(
        points,
        key=lambda point: point.observation_date,
    )

    features: list[FeaturePoint] = []

    for index, point in enumerate(ordered):
        delta_1 = _delta(
            ordered,
            index,
            1,
        )

        delta_3 = _delta(
            ordered,
            index,
            3,
        )

        pct_change_1 = _pct_change(
            ordered,
            index,
            1,
        )

        pct_change_3 = _pct_change(
            ordered,
            index,
            3,
        )

        pct_change_12 = _pct_change(
            ordered,
            index,
            12,
        )

        (
            rolling_mean,
            rolling_std,
            z_score,
        ) = _rolling_statistics(
            ordered,
            index,
            rolling_window,
        )

        previous_delta = _delta(
            ordered,
            index - 1,
            1,
        )

        acceleration = (
            delta_1 - previous_delta
            if (delta_1 is not None and previous_delta is not None)
            else None
        )

        anomaly_score = abs(z_score) if z_score is not None else None

        features.append(
            FeaturePoint(
                observation_date=(point.observation_date),
                value=point.value,
                delta_1=delta_1,
                delta_3=delta_3,
                pct_change_1=pct_change_1,
                pct_change_3=pct_change_3,
                pct_change_12=pct_change_12,
                rolling_mean=rolling_mean,
                rolling_std=rolling_std,
                z_score=z_score,
                acceleration=acceleration,
                anomaly_score=anomaly_score,
            )
        )

    return features


def anomalies(
    features: list[FeaturePoint],
    *,
    threshold: float = 2.0,
) -> list[FeaturePoint]:
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    return [
        point
        for point in features
        if (point.anomaly_score is not None and point.anomaly_score >= threshold)
    ]
