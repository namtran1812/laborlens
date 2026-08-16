from datetime import date

from laborlens.analysis.regime import RegimePoint
from laborlens.research.claims import (
    CandidateClaim,
)
from laborlens.research.episodes import (
    ClaimEpisode,
)
from laborlens.research.evidence import (
    EvidenceBundle,
)
from laborlens.research.research_bundle import (
    ProvenanceItem,
    build_research_bundle,
    find_historical_analogs,
    historical_percentile,
)
from laborlens.research.skeptic import (
    SkepticVerdict,
)


def regime_point(
    month: int,
    score: float,
) -> RegimePoint:
    return RegimePoint(
        observation_date=date(
            2024,
            month,
            1,
        ),
        raw_score=score,
        score=score,
        raw_dispersion=0.2,
        dispersion=0.2,
        signals_used=5,
        coverage=1.0,
        label="test",
        contributions={
            "A": score,
        },
        smoothed_contributions={
            "A": score,
        },
    )


def episode(
    name: str,
    month: int,
    score: float,
) -> ClaimEpisode:
    claim = CandidateClaim(
        claim_id=name,
        observation_date=date(
            2024,
            month,
            1,
        ),
        claim_type="broad_contraction",
        headline="test",
        score=score,
        dispersion=0.2,
        coverage=1.0,
        confidence=0.9,
        evidence=(),
    )

    return ClaimEpisode(
        episode_id=name,
        claim_type="broad_contraction",
        start_date=claim.observation_date,
        end_date=claim.observation_date,
        representative=claim,
        duration_months=1,
        peak_confidence=0.9,
        claims=(claim,),
    )


def test_historical_percentile() -> None:
    regimes = [
        regime_point(1, -0.2),
        regime_point(2, -0.5),
        regime_point(3, -1.0),
    ]

    result = historical_percentile(
        -0.5,
        regimes,
    )

    assert result == 2 / 3


def test_historical_analogs_exclude_self() -> None:
    target = episode(
        "target",
        1,
        -0.7,
    )

    other = episode(
        "other",
        2,
        -0.6,
    )

    analogs = find_historical_analogs(
        target,
        [
            target,
            other,
        ],
    )

    assert len(analogs) == 1
    assert analogs[0].start_date == date(
        2024,
        2,
        1,
    )


def test_build_research_bundle() -> None:
    target = episode(
        "target",
        2,
        -0.7,
    )

    evidence = EvidenceBundle(
        episode_id="target",
        claim_type="broad_contraction",
        start_date=date(
            2024,
            2,
            1,
        ),
        end_date=date(
            2024,
            2,
            1,
        ),
        headline="test",
        score=-0.7,
        dispersion=0.2,
        coverage=1.0,
        confidence=0.9,
        supporting=(),
        opposing=(),
        breadth=1.0,
    )

    skeptic = SkepticVerdict(
        verdict="supported",
        score=0.9,
        findings=(),
    )

    provenance = [
        ProvenanceItem(
            series_id="PAYEMS",
            observation_date=date(
                2024,
                2,
                1,
            ),
            value=100.0,
            realtime_start=date(
                2024,
                3,
                1,
            ),
            realtime_end=date(
                2024,
                3,
                1,
            ),
        )
    ]

    bundle = build_research_bundle(
        episode=target,
        evidence=evidence,
        skeptic=skeptic,
        regimes=[
            regime_point(1, -0.3),
            regime_point(2, -0.7),
        ],
        all_episodes=[
            target,
        ],
        provenance=provenance,
    )

    assert bundle.duration_months == 1
    assert bundle.skeptic.verdict == "supported"
    assert len(bundle.provenance) == 1


def test_bundle_tracks_historical_scope() -> None:
    target = episode(
        "target-scope",
        2,
        -0.7,
    )

    evidence = EvidenceBundle(
        episode_id="target-scope",
        claim_type="broad_contraction",
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 1),
        headline="test",
        score=-0.7,
        dispersion=0.2,
        coverage=1.0,
        confidence=0.9,
        supporting=(),
        opposing=(),
        breadth=1.0,
    )

    skeptic = SkepticVerdict(
        verdict="supported",
        score=0.9,
        findings=(),
    )

    bundle = build_research_bundle(
        episode=target,
        evidence=evidence,
        skeptic=skeptic,
        regimes=[
            regime_point(1, -0.3),
            regime_point(2, -0.7),
            regime_point(3, -0.4),
        ],
        all_episodes=[target],
        provenance=[],
    )

    assert bundle.comparable_observation_count == 3
    assert bundle.historical_start_date == date(2024, 1, 1)
    assert bundle.historical_end_date == date(2024, 3, 1)
