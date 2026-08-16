from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from math import sqrt
from statistics import fmean


@dataclass(frozen=True)
class SignalSpec:
    series_id: str
    transform: str
    direction: float
    frequency: str = "monthly"


@dataclass(frozen=True)
class SignalValue:
    observation_date: date
    raw_value: float
    change: float | None
    z_score: float | None
    contribution: float | None


@dataclass(frozen=True)
class RegimePoint:
    observation_date: date
    raw_score: float
    score: float
    raw_dispersion: float
    dispersion: float
    signals_used: int
    coverage: float
    label: str
    contributions: dict[str, float]
    smoothed_contributions: dict[str, float]


DEFAULT_SPECS = {
    "PAYEMS": SignalSpec(
        series_id="PAYEMS",
        transform="pct",
        direction=1.0,
    ),
    "JTSHIR": SignalSpec(
        series_id="JTSHIR",
        transform="pct",
        direction=1.0,
    ),
    "JTSJOL": SignalSpec(
        series_id="JTSJOL",
        transform="pct",
        direction=1.0,
    ),
    "UNRATE": SignalSpec(
        series_id="UNRATE",
        transform="diff",
        direction=-1.0,
    ),
    "ICSA": SignalSpec(
        series_id="ICSA",
        transform="pct",
        direction=-1.0,
        frequency="weekly",
    ),
}


def monthly_average(
    points: list[tuple[date, float]],
) -> list[tuple[date, float]]:
    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)

    for observation_date, value in points:
        buckets[
            (
                observation_date.year,
                observation_date.month,
            )
        ].append(value)

    result = []

    for (year, month), values in sorted(buckets.items()):
        result.append(
            (
                date(year, month, 1),
                fmean(values),
            )
        )

    return result


def _change(
    current: float,
    previous: float,
    transform: str,
) -> float | None:
    if transform == "diff":
        return current - previous

    if transform == "pct":
        if previous == 0:
            return None

        return (current - previous) / abs(previous)

    raise ValueError(f"unknown transform: {transform}")


def _z_score(
    values: list[float],
) -> float:
    mean = fmean(values)

    variance = fmean((value - mean) ** 2 for value in values)

    std = sqrt(variance)

    if std == 0:
        return 0.0

    return (values[-1] - mean) / std


def compute_signal(
    points: list[tuple[date, float]],
    spec: SignalSpec,
    *,
    window: int = 24,
) -> list[SignalValue]:
    if window < 2:
        raise ValueError("window must be at least 2")

    ordered = sorted(points)

    if spec.frequency == "weekly":
        ordered = monthly_average(ordered)

    changes: list[float | None] = [None]

    for index in range(
        1,
        len(ordered),
    ):
        changes.append(
            _change(
                ordered[index][1],
                ordered[index - 1][1],
                spec.transform,
            )
        )

    result = []

    for index, (
        observation_date,
        raw_value,
    ) in enumerate(ordered):
        change = changes[index]

        z_score = None
        contribution = None

        start = index - window + 1

        if change is not None and start >= 1:
            history = [value for value in changes[start : index + 1] if value is not None]

            if len(history) == window:
                z_score = _z_score(history)

                contribution = z_score * spec.direction

                if abs(contribution) < 1e-12:
                    contribution = 0.0

        result.append(
            SignalValue(
                observation_date=observation_date,
                raw_value=raw_value,
                change=change,
                z_score=z_score,
                contribution=contribution,
            )
        )

    return result


def classify_regime(
    score: float,
    dispersion: float,
) -> str:
    if dispersion >= 1.5:
        return "divergent"

    if score >= 1.0:
        return "strong_expansion"

    if score >= 0.35:
        return "expansion"

    if score <= -1.0:
        return "strong_contraction"

    if score <= -0.35:
        return "contraction"

    return "neutral"


def compute_regime(
    signals: dict[
        str,
        list[SignalValue],
    ],
    *,
    min_signals: int = 3,
    smoothing_window: int = 3,
) -> list[RegimePoint]:
    if smoothing_window < 1:
        raise ValueError("smoothing_window must be at least 1")

    dates: set[date] = set()

    lookup: dict[
        str,
        dict[date, SignalValue],
    ] = {}

    for series_id, values in signals.items():
        lookup[series_id] = {value.observation_date: value for value in values}

        dates.update(lookup[series_id])

    expected_signals = len(signals)

    provisional: list[
        tuple[
            date,
            float,
            float,
            int,
            float,
            dict[str, float],
        ]
    ] = []

    for observation_date in sorted(dates):
        contributions = {}

        for series_id, values in lookup.items():
            value = values.get(observation_date)

            if value is not None and value.contribution is not None:
                contributions[series_id] = value.contribution

        if len(contributions) < min_signals:
            continue

        values = list(contributions.values())

        raw_score = fmean(values)

        variance = fmean((value - raw_score) ** 2 for value in values)

        dispersion = sqrt(variance)

        coverage = len(values) / expected_signals if expected_signals else 0.0

        provisional.append(
            (
                observation_date,
                raw_score,
                dispersion,
                len(values),
                coverage,
                contributions,
            )
        )

    result: list[RegimePoint] = []

    for index, (
        observation_date,
        raw_score,
        dispersion,
        signals_used,
        coverage,
        contributions,
    ) in enumerate(provisional):
        start_index = max(
            0,
            index - smoothing_window + 1,
        )

        history = [item[1] for item in provisional[start_index : index + 1]]

        smoothed_score = fmean(history)

        contribution_history: dict[str, list[float]] = defaultdict(list)

        for history_item in provisional[start_index : index + 1]:
            for series_id, value in history_item[5].items():
                contribution_history[series_id].append(value)

        smoothed_contributions = {
            series_id: fmean(values) for series_id, values in contribution_history.items()
        }

        smoothed_values = list(smoothed_contributions.values())

        smoothed_variance = fmean((value - smoothed_score) ** 2 for value in smoothed_values)

        smoothed_dispersion = sqrt(smoothed_variance)

        if coverage < 0.8:
            label = "low_coverage"

        else:
            label = classify_regime(
                smoothed_score,
                smoothed_dispersion,
            )

        result.append(
            RegimePoint(
                observation_date=(observation_date),
                raw_score=raw_score,
                score=smoothed_score,
                raw_dispersion=dispersion,
                dispersion=smoothed_dispersion,
                signals_used=signals_used,
                coverage=coverage,
                label=label,
                contributions=contributions,
                smoothed_contributions=smoothed_contributions,
            )
        )

    return result
