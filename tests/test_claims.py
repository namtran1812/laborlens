from datetime import date

import pytest

from laborlens.analysis.regime import RegimePoint
from laborlens.research.claims import (
    discover_claim,
    discover_claims,
)


def regime(
    *,
    score: float,
    dispersion: float,
    coverage: float = 1.0,
) -> RegimePoint:
    direction = 1.0 if score > 0 else -1.0

    contributions = {
        "PAYEMS": direction * 1.0,
        "JTSHIR": direction * 1.5,
        "JTSJOL": direction * 0.8,
        "UNRATE": direction * 1.2,
        "ICSA": direction * 0.9,
    }

    return RegimePoint(
        observation_date=date(
            2024,
            6,
            1,
        ),
        raw_score=score,
        score=score,
        raw_dispersion=dispersion,
        dispersion=dispersion,
        signals_used=5,
        coverage=coverage,
        label="test",
        contributions=contributions,
        smoothed_contributions=contributions,
    )


def test_discovers_broad_contraction() -> None:
    claim = discover_claim(
        regime(
            score=-0.8,
            dispersion=0.4,
        )
    )

    assert claim is not None
    assert claim.claim_type == "broad_contraction"


def test_discovers_broad_expansion() -> None:
    claim = discover_claim(
        regime(
            score=0.8,
            dispersion=0.4,
        )
    )

    assert claim is not None
    assert claim.claim_type == "broad_expansion"


def test_discovers_divergence() -> None:
    base = regime(
        score=0.0,
        dispersion=1.4,
    )

    point = RegimePoint(
        observation_date=base.observation_date,
        raw_score=0.0,
        score=0.0,
        raw_dispersion=1.4,
        dispersion=1.4,
        signals_used=5,
        coverage=1.0,
        label="test",
        contributions={
            "PAYEMS": -1.2,
            "JTSHIR": 1.4,
            "JTSJOL": 1.0,
            "UNRATE": -0.9,
            "ICSA": -0.6,
        },
        smoothed_contributions={
            "PAYEMS": -1.2,
            "JTSHIR": 1.4,
            "JTSJOL": 1.0,
            "UNRATE": -0.9,
            "ICSA": -0.6,
        },
    )

    claim = discover_claim(point)

    assert claim is not None

    assert claim.claim_type == "signal_divergence"


def test_rejects_low_coverage() -> None:
    claim = discover_claim(
        regime(
            score=-1.0,
            dispersion=0.2,
            coverage=0.6,
        )
    )

    assert claim is None


def test_evidence_is_ranked() -> None:
    claim = discover_claim(
        regime(
            score=-0.8,
            dispersion=0.4,
        )
    )

    assert claim is not None

    assert claim.evidence[0].series_id == "JTSHIR"


def test_confidence_filter() -> None:
    claims = discover_claims(
        [
            regime(
                score=-0.4,
                dispersion=0.7,
            )
        ],
        min_confidence=0.99,
    )

    assert claims == []


def test_invalid_confidence() -> None:
    with pytest.raises(
        ValueError,
        match="min_confidence",
    ):
        discover_claims(
            [],
            min_confidence=1.5,
        )


def test_broad_claim_requires_directional_breadth() -> None:
    point = regime(
        score=-0.8,
        dispersion=0.4,
    )

    point = RegimePoint(
        observation_date=point.observation_date,
        raw_score=point.raw_score,
        score=point.score,
        raw_dispersion=point.raw_dispersion,
        dispersion=point.dispersion,
        signals_used=point.signals_used,
        coverage=point.coverage,
        label=point.label,
        contributions=point.contributions,
        smoothed_contributions={
            "PAYEMS": -1.0,
            "JTSHIR": 0.5,
            "JTSJOL": 0.4,
            "UNRATE": -0.2,
            "ICSA": 0.3,
        },
    )

    claim = discover_claim(point)

    assert claim is None or claim.claim_type != "broad_contraction"


def test_claim_evidence_uses_smoothed_contributions() -> None:
    point = regime(
        score=-0.8,
        dispersion=0.4,
    )

    point = RegimePoint(
        observation_date=point.observation_date,
        raw_score=point.raw_score,
        score=point.score,
        raw_dispersion=point.raw_dispersion,
        dispersion=point.dispersion,
        signals_used=point.signals_used,
        coverage=point.coverage,
        label=point.label,
        contributions={
            "PAYEMS": 2.0,
            "JTSHIR": 2.0,
            "JTSJOL": 2.0,
            "UNRATE": 2.0,
            "ICSA": 2.0,
        },
        smoothed_contributions={
            "PAYEMS": -0.8,
            "JTSHIR": -1.6,
            "JTSJOL": -0.6,
            "UNRATE": -1.0,
            "ICSA": -0.7,
        },
    )

    claim = discover_claim(point)

    assert claim is not None

    assert claim.evidence[0].series_id == "JTSHIR"

    assert claim.evidence[0].contribution == -1.6


def test_divergence_requires_opposing_signals() -> None:
    point = regime(
        score=-0.2,
        dispersion=1.4,
    )

    point = RegimePoint(
        observation_date=point.observation_date,
        raw_score=point.raw_score,
        score=point.score,
        raw_dispersion=1.4,
        dispersion=1.4,
        signals_used=5,
        coverage=1.0,
        label="test",
        contributions=point.contributions,
        smoothed_contributions={
            "PAYEMS": -2.0,
            "JTSHIR": -1.5,
            "JTSJOL": -1.0,
            "UNRATE": -0.8,
            "ICSA": -0.4,
        },
    )

    claim = discover_claim(point)

    assert claim is None or claim.claim_type != "signal_divergence"
