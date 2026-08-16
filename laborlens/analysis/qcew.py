from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class QcewComparisonType(StrEnum):
    LOCAL_CONTRACTION = "local_contraction"
    RELATIVE_RESILIENCE = "relative_resilience"
    RELATIVE_UNDERPERFORMANCE = "relative_underperformance"
    RELATIVE_OUTPERFORMANCE = "relative_outperformance"
    LOCAL_EXPANSION = "local_expansion"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class QcewIndustryComparison:
    industry_code: str
    industry_title: str

    local_employment: int
    national_employment: int

    local_yoy_growth: float | None
    national_yoy_growth: float | None

    relative_growth: float | None

    local_location_quotient: float | None

    comparison_type: QcewComparisonType

    weakening_score: float | None


def classify_comparison(
    *,
    local_growth: float | None,
    national_growth: float | None,
) -> QcewComparisonType:
    if local_growth is None or national_growth is None:
        return QcewComparisonType.INSUFFICIENT_DATA

    relative_growth = local_growth - national_growth

    if local_growth < 0:
        if relative_growth < 0:
            return QcewComparisonType.LOCAL_CONTRACTION

        if relative_growth > 0:
            return QcewComparisonType.RELATIVE_RESILIENCE

        return QcewComparisonType.LOCAL_CONTRACTION

    if relative_growth < 0:
        return QcewComparisonType.RELATIVE_UNDERPERFORMANCE

    if relative_growth > 0:
        return QcewComparisonType.RELATIVE_OUTPERFORMANCE

    return QcewComparisonType.LOCAL_EXPANSION


def weakening_score(
    *,
    local_growth: float | None,
    national_growth: float | None,
    location_quotient: float | None,
) -> float | None:
    if local_growth is None or national_growth is None:
        return None

    relative_growth = local_growth - national_growth

    importance = max(
        location_quotient or 1.0,
        0.25,
    )

    return -relative_growth * importance
