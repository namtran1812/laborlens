from datetime import date

from laborlens.research.claims import CandidateClaim
from laborlens.research.episodes import ClaimEpisode
from laborlens.research.evidence import (
    EvidenceBundle,
    EvidenceSignal,
)
from laborlens.research.research_bundle import ResearchBundle
from laborlens.research.skeptic import SkepticVerdict
from laborlens.writer.prompt import build_writer_input
from laborlens.writer.verifier import verify_article_numbers


def bundle() -> ResearchBundle:
    claim = CandidateClaim(
        claim_id="claim",
        observation_date=date(
            2024,
            6,
            1,
        ),
        claim_type="broad_contraction",
        headline=("Labor-market indicators are weakening broadly"),
        score=-0.566,
        dispersion=0.29,
        coverage=1.0,
        confidence=0.872,
        evidence=(),
    )

    episode = ClaimEpisode(
        episode_id="episode",
        claim_type="broad_contraction",
        start_date=date(
            2024,
            6,
            1,
        ),
        end_date=date(
            2024,
            8,
            1,
        ),
        representative=claim,
        duration_months=3,
        peak_confidence=0.872,
        claims=(claim,),
    )

    evidence = EvidenceBundle(
        episode_id="episode",
        claim_type="broad_contraction",
        start_date=episode.start_date,
        end_date=episode.end_date,
        headline=claim.headline,
        score=-0.566,
        dispersion=0.29,
        coverage=1.0,
        confidence=0.872,
        supporting=(
            EvidenceSignal(
                series_id="PAYEMS",
                contribution=-1.135,
                direction="negative",
                magnitude=1.135,
            ),
        ),
        opposing=(),
        breadth=1.0,
    )

    return ResearchBundle(
        episode_id="episode",
        claim=claim,
        episode=episode,
        evidence=evidence,
        skeptic=SkepticVerdict(
            verdict="supported",
            score=0.865,
            findings=(),
        ),
        duration_months=3,
        mean_episode_score=-0.505,
        peak_episode_score=-0.566,
        historical_percentile=0.868,
        comparable_observation_count=10,
        historical_start_date=date(2023, 1, 1),
        historical_end_date=date(2024, 6, 1),
        historical_analogs=(),
        provenance=(),
    )


def test_writer_input_contains_verified_bundle() -> None:
    text = build_writer_input(bundle())

    assert "PAYEMS" in text
    assert "0.868" in text
    assert "broad_contraction" in text


def test_verifier_accepts_supported_number() -> None:
    result = verify_article_numbers(
        "The peak score was -0.566.",
        bundle(),
    )

    assert result.passed


def test_verifier_accepts_bundle_percent() -> None:
    result = verify_article_numbers(
        "The historical percentile was 86.8%.",
        bundle(),
    )

    assert result.passed


def test_verifier_rejects_invented_number() -> None:
    result = verify_article_numbers(
        "Employment declined by 17.4%.",
        bundle(),
    )

    assert not result.passed

    assert "17.4%" in (result.unsupported_numbers)


def test_verifier_accepts_bundle_date() -> None:
    result = verify_article_numbers(
        "The episode began on 2024-06-01.",
        bundle(),
    )

    assert result.passed


def test_verifier_rejects_invented_date() -> None:
    result = verify_article_numbers(
        "The episode began on 2030-01-01.",
        bundle(),
    )

    assert not result.passed

    assert "2030-01-01" in (result.unsupported_dates)


def test_deterministic_writer_produces_grounded_article() -> None:
    from laborlens.writer.deterministic_writer import (
        write_deterministic_article,
    )

    research = bundle()

    article = write_deterministic_article(research)

    assert "# Labor-market indicators" in article
    assert "PAYEMS" in article
    assert "-1.14" in article
    assert "2024-06-01" in article

    result = verify_article_numbers(
        article,
        research,
    )

    assert result.passed
