import pytest

from laborlens.analysis.qcew import (
    weakening_score,
)


def test_weakening_score_penalizes_relative_decline():
    result = weakening_score(
        local_growth=-4.0,
        national_growth=1.0,
        location_quotient=1.2,
    )

    assert result == pytest.approx(6.0)


def test_weakening_score_returns_none_without_growth():
    assert (
        weakening_score(
            local_growth=None,
            national_growth=1.0,
            location_quotient=1.0,
        )
        is None
    )


def test_location_quotient_weights_local_importance():
    high = weakening_score(
        local_growth=-2.0,
        national_growth=0.0,
        location_quotient=2.0,
    )

    normal = weakening_score(
        local_growth=-2.0,
        national_growth=0.0,
        location_quotient=1.0,
    )

    assert high is not None
    assert normal is not None
    assert high > normal


def test_classify_local_contraction():
    from laborlens.analysis.qcew import (
        QcewComparisonType,
        classify_comparison,
    )

    assert (
        classify_comparison(
            local_growth=-4.0,
            national_growth=2.0,
        )
        == QcewComparisonType.LOCAL_CONTRACTION
    )


def test_classify_relative_underperformance():
    from laborlens.analysis.qcew import (
        QcewComparisonType,
        classify_comparison,
    )

    assert (
        classify_comparison(
            local_growth=1.0,
            national_growth=4.0,
        )
        == QcewComparisonType.RELATIVE_UNDERPERFORMANCE
    )


def test_classify_relative_outperformance():
    from laborlens.analysis.qcew import (
        QcewComparisonType,
        classify_comparison,
    )

    assert (
        classify_comparison(
            local_growth=5.0,
            national_growth=2.0,
        )
        == QcewComparisonType.RELATIVE_OUTPERFORMANCE
    )
