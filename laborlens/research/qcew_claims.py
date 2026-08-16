from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from laborlens.analysis.qcew import (
    QcewComparisonType,
    QcewIndustryComparison,
)


class QcewClaimType(StrEnum):
    LOCAL_CONTRACTION = "local_contraction"
    RELATIVE_RESILIENCE = "relative_resilience"
    RELATIVE_UNDERPERFORMANCE = "relative_underperformance"
    LOCAL_OUTPERFORMANCE = "local_outperformance"


@dataclass(frozen=True)
class QcewClaim:
    claim_type: QcewClaimType

    area_fips: str
    area_title: str

    industry_code: str
    industry_title: str

    year: int
    quarter: int

    local_employment: int
    national_employment: int

    local_yoy_growth: float
    national_yoy_growth: float
    relative_gap: float

    location_quotient: float | None

    strength: float
    headline: str
    evidence_text: str


def _clean_industry_title(
    title: str,
) -> str:
    prefix = "NAICS "

    if title.startswith(prefix):
        parts = title.split(
            " ",
            2,
        )

        if len(parts) == 3:
            return parts[2]

    return title


def _strength(
    *,
    relative_gap: float,
    location_quotient: float | None,
    local_employment: int,
) -> float:
    """
    Deterministic ranking score.

    Not a statistical probability.
    """
    importance = max(
        location_quotient or 1.0,
        0.5,
    )

    employment_weight = min(
        1.0,
        local_employment / 50_000,
    )

    raw = abs(relative_gap) * importance * (0.5 + 0.5 * employment_weight)

    return raw


def generate_qcew_claims(
    comparisons: list[QcewIndustryComparison],
    *,
    area_fips: str,
    area_title: str,
    year: int,
    quarter: int,
    minimum_employment: int = 10_000,
    minimum_relative_gap: float = 2.0,
    minimum_contraction: float = 1.0,
) -> list[QcewClaim]:
    claims: list[QcewClaim] = []

    for comparison in comparisons:
        local_growth = comparison.local_yoy_growth
        national_growth = comparison.national_yoy_growth
        relative_gap = comparison.relative_growth

        if local_growth is None or national_growth is None or relative_gap is None:
            continue

        if comparison.local_employment < minimum_employment:
            continue

        title = _clean_industry_title(comparison.industry_title)

        claim_type: QcewClaimType | None = None
        headline: str | None = None
        evidence: str | None = None

        if (
            comparison.comparison_type == QcewComparisonType.LOCAL_CONTRACTION
            and local_growth <= -minimum_contraction
            and relative_gap <= -minimum_relative_gap
        ):
            claim_type = QcewClaimType.LOCAL_CONTRACTION

            headline = (
                f"{area_title} {title} employment contracted faster than the national industry."
            )

            evidence = (
                f"Employment fell "
                f"{abs(local_growth):.1f}% "
                f"year over year in {area_title}, "
                f"compared with "
                f"{national_growth:.1f}% nationally, "
                f"representing {abs(relative_gap):.1f} "
                f"percentage-point relative "
                f"deterioration."
            )

        elif (
            comparison.comparison_type == QcewComparisonType.RELATIVE_RESILIENCE
            and relative_gap >= minimum_relative_gap
        ):
            claim_type = QcewClaimType.RELATIVE_RESILIENCE

            headline = (
                f"{area_title} {title} employment "
                f"contracted less sharply than the "
                f"national industry."
            )

            evidence = (
                f"Employment fell "
                f"{abs(local_growth):.1f}% "
                f"year over year in {area_title}, "
                f"compared with a "
                f"{abs(national_growth):.1f}% "
                f"national decline, "
                f"a {relative_gap:.1f} "
                f"percentage-point relative "
                f"advantage."
            )

        elif (
            comparison.comparison_type == QcewComparisonType.RELATIVE_UNDERPERFORMANCE
            and relative_gap <= -minimum_relative_gap
        ):
            claim_type = QcewClaimType.RELATIVE_UNDERPERFORMANCE

            headline = (
                f"{area_title} {title} employment grew more slowly than the national industry."
            )

            evidence = (
                f"Employment grew "
                f"{local_growth:.1f}% "
                f"year over year in {area_title}, "
                f"versus "
                f"{national_growth:.1f}% nationally, "
                f"lagging by "
                f"{abs(relative_gap):.1f} "
                f"percentage points."
            )

        elif (
            comparison.comparison_type == QcewComparisonType.RELATIVE_OUTPERFORMANCE
            and local_growth >= 0
            and relative_gap >= minimum_relative_gap
        ):
            claim_type = QcewClaimType.LOCAL_OUTPERFORMANCE

            headline = f"{area_title} {title} employment outperformed the national industry."

            if national_growth < 0:
                evidence = (
                    f"Employment grew "
                    f"{local_growth:.1f}% "
                    f"year over year in {area_title}, "
                    f"while national employment fell "
                    f"{abs(national_growth):.1f}%, "
                    f"a {relative_gap:.1f} "
                    f"percentage-point relative "
                    f"advantage."
                )
            else:
                evidence = (
                    f"Employment grew "
                    f"{local_growth:.1f}% "
                    f"year over year in {area_title}, "
                    f"versus "
                    f"{national_growth:.1f}% nationally, "
                    f"a {relative_gap:.1f} "
                    f"percentage-point relative "
                    f"advantage."
                )

        if claim_type is None or headline is None or evidence is None:
            continue

        claims.append(
            QcewClaim(
                claim_type=claim_type,
                area_fips=area_fips,
                area_title=area_title,
                industry_code=(comparison.industry_code),
                industry_title=title,
                year=year,
                quarter=quarter,
                local_employment=(comparison.local_employment),
                national_employment=(comparison.national_employment),
                local_yoy_growth=local_growth,
                national_yoy_growth=national_growth,
                relative_gap=relative_gap,
                location_quotient=(comparison.local_location_quotient),
                strength=_strength(
                    relative_gap=relative_gap,
                    location_quotient=(comparison.local_location_quotient),
                    local_employment=(comparison.local_employment),
                ),
                headline=headline,
                evidence_text=evidence,
            )
        )

    return sorted(
        claims,
        key=lambda claim: claim.strength,
        reverse=True,
    )
