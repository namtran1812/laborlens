from laborlens.research.qcew_context import (
    CrossSectionalClaim,
    CrossSectionalContext,
)


def test_cross_sectional_context_preserves_validated_claim():
    claim = CrossSectionalClaim(
        claim_type="local_contraction",
        industry_code="561330",
        industry_title=("Professional employer organizations"),
        local_employment=56_286,
        local_yoy_growth=-14.2,
        national_yoy_growth=-5.5,
        relative_gap=-8.7,
        location_quotient=2.14,
        strength=18.62,
        skeptic_verdict="supported",
        skeptic_score=1.0,
        headline="Example headline",
        evidence_text=("Employment fell 14.2% locally."),
    )

    context = CrossSectionalContext(
        area_fips="12000",
        area_title="Florida -- Statewide",
        year=2024,
        quarter=2,
        industry_level=6,
        context_mode="retrospective",
        data_release_date=None,
        requested_as_of_date=None,
        claims=(claim,),
    )

    assert context.area_fips == "12000"
    assert len(context.claims) == 1
    assert context.claims[0].relative_gap == -8.7


def test_point_in_time_context_tracks_release_metadata():
    from datetime import date

    context = CrossSectionalContext(
        area_fips="12000",
        area_title="Florida -- Statewide",
        year=2023,
        quarter=4,
        industry_level=6,
        context_mode="point_in_time",
        data_release_date=date(
            2024,
            6,
            5,
        ),
        requested_as_of_date=date(
            2024,
            9,
            1,
        ),
        claims=(),
    )

    assert context.data_release_date == date(2024, 6, 5)
    assert context.requested_as_of_date == date(2024, 9, 1)
    assert context.context_mode == "point_in_time"
