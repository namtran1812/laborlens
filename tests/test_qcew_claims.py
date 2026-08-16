from laborlens.analysis.qcew import (
    QcewComparisonType,
    QcewIndustryComparison,
)
from laborlens.research.qcew_claims import (
    QcewClaimType,
    generate_qcew_claims,
)
from laborlens.research.qcew_skeptic import (
    QcewSkepticVerdict,
    evaluate_qcew_claim,
)


def comparison(
    *,
    local_growth: float,
    national_growth: float,
    comparison_type: QcewComparisonType,
) -> QcewIndustryComparison:
    return QcewIndustryComparison(
        industry_code="561330",
        industry_title=("NAICS 561330 Professional employer organizations"),
        local_employment=56_286,
        national_employment=500_000,
        local_yoy_growth=local_growth,
        national_yoy_growth=national_growth,
        relative_growth=(local_growth - national_growth),
        local_location_quotient=2.14,
        comparison_type=comparison_type,
        weakening_score=18.6,
    )


def test_generates_local_contraction_claim():
    claims = generate_qcew_claims(
        [
            comparison(
                local_growth=-14.2,
                national_growth=-5.5,
                comparison_type=(QcewComparisonType.LOCAL_CONTRACTION),
            )
        ],
        area_fips="12000",
        area_title="Florida -- Statewide",
        year=2024,
        quarter=2,
    )

    assert len(claims) == 1

    claim = claims[0]

    assert claim.claim_type == QcewClaimType.LOCAL_CONTRACTION

    assert claim.relative_gap == -8.7


def test_underperformance_not_called_contraction():
    claims = generate_qcew_claims(
        [
            comparison(
                local_growth=1.3,
                national_growth=4.8,
                comparison_type=(QcewComparisonType.RELATIVE_UNDERPERFORMANCE),
            )
        ],
        area_fips="12000",
        area_title="Florida -- Statewide",
        year=2024,
        quarter=2,
    )

    assert len(claims) == 1

    assert claims[0].claim_type == QcewClaimType.RELATIVE_UNDERPERFORMANCE


def test_skeptic_supports_strong_claim():
    claim = generate_qcew_claims(
        [
            comparison(
                local_growth=-14.2,
                national_growth=-5.5,
                comparison_type=(QcewComparisonType.LOCAL_CONTRACTION),
            )
        ],
        area_fips="12000",
        area_title="Florida -- Statewide",
        year=2024,
        quarter=2,
    )[0]

    result = evaluate_qcew_claim(claim)

    assert result.verdict == QcewSkepticVerdict.SUPPORTED


def test_claim_type_includes_relative_resilience():
    from laborlens.research.qcew_claims import (
        QcewClaimType,
    )

    assert QcewClaimType.RELATIVE_RESILIENCE == "relative_resilience"
