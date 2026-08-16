from datetime import date

from laborlens.research.claims import (
    CandidateClaim,
    EvidenceItem,
)
from laborlens.research.episodes import (
    ClaimEpisode,
)
from laborlens.research.evidence import (
    build_evidence_bundle,
)
from laborlens.research.skeptic import (
    review_evidence,
)


def episode(
    evidence: tuple[
        EvidenceItem,
        ...,
    ],
) -> ClaimEpisode:
    claim = CandidateClaim(
        claim_id="test",
        observation_date=date(
            2024,
            6,
            1,
        ),
        claim_type="broad_contraction",
        headline=("Labor-market indicators are weakening broadly"),
        score=-0.6,
        dispersion=0.3,
        coverage=1.0,
        confidence=0.9,
        evidence=evidence,
    )

    return ClaimEpisode(
        episode_id="episode-test",
        claim_type=("broad_contraction"),
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
        peak_confidence=0.9,
        claims=(claim,),
    )


def test_bundle_separates_support_and_opposition() -> None:
    bundle = build_evidence_bundle(
        episode(
            (
                EvidenceItem(
                    "PAYEMS",
                    -1.2,
                ),
                EvidenceItem(
                    "JTSHIR",
                    -0.8,
                ),
                EvidenceItem(
                    "JTSJOL",
                    0.5,
                ),
            )
        )
    )

    assert len(bundle.supporting) == 2

    assert len(bundle.opposing) == 1


def test_supported_episode_passes_skeptic() -> None:
    bundle = build_evidence_bundle(
        episode(
            (
                EvidenceItem(
                    "PAYEMS",
                    -1.2,
                ),
                EvidenceItem(
                    "JTSHIR",
                    -1.0,
                ),
                EvidenceItem(
                    "JTSJOL",
                    -0.8,
                ),
                EvidenceItem(
                    "UNRATE",
                    -0.7,
                ),
                EvidenceItem(
                    "ICSA",
                    -0.6,
                ),
            )
        )
    )

    verdict = review_evidence(bundle)

    assert verdict.verdict == "supported"


def test_counter_signal_lowers_verdict() -> None:
    bundle = build_evidence_bundle(
        episode(
            (
                EvidenceItem(
                    "PAYEMS",
                    -0.4,
                ),
                EvidenceItem(
                    "JTSHIR",
                    -0.3,
                ),
                EvidenceItem(
                    "JTSJOL",
                    1.5,
                ),
                EvidenceItem(
                    "UNRATE",
                    1.2,
                ),
                EvidenceItem(
                    "ICSA",
                    -0.2,
                ),
            )
        )
    )

    verdict = review_evidence(bundle)

    assert verdict.verdict != "supported"
