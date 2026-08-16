from __future__ import annotations

from dataclasses import dataclass

from laborlens.research.evidence import (
    EvidenceBundle,
)


@dataclass(frozen=True)
class SkepticFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class SkepticVerdict:
    verdict: str
    score: float
    findings: tuple[SkepticFinding, ...]


def review_evidence(
    bundle: EvidenceBundle,
) -> SkepticVerdict:
    findings = []

    penalty = 0.0

    if bundle.coverage < 0.8:
        findings.append(
            SkepticFinding(
                code="low_coverage",
                severity="high",
                message=("Too few indicators are available to support the claim."),
            )
        )

        penalty += 0.40

    if bundle.breadth < 0.8:
        findings.append(
            SkepticFinding(
                code="weak_breadth",
                severity="high",
                message=("The claim is not supported by enough independent indicators."),
            )
        )

        penalty += 0.35

    if bundle.dispersion > 0.75:
        findings.append(
            SkepticFinding(
                code="high_dispersion",
                severity="medium",
                message=("Signal disagreement is high relative to a broad-direction claim."),
            )
        )

        penalty += 0.20

    if bundle.opposing:
        strongest = max(
            bundle.opposing,
            key=lambda item: item.magnitude,
        )

        findings.append(
            SkepticFinding(
                code="counter_signal",
                severity="medium",
                message=(f"{strongest.series_id} points against the headline."),
            )
        )

        penalty += min(
            0.25,
            0.10 + strongest.magnitude * 0.05,
        )

    support_strength = min(
        1.0,
        sum(item.magnitude for item in bundle.supporting) / 5.0,
    )

    score = 0.55 * bundle.confidence + 0.30 * bundle.breadth + 0.15 * support_strength - penalty

    score = max(
        0.0,
        min(1.0, score),
    )

    if score >= 0.75:
        verdict = "supported"

    elif score >= 0.50:
        verdict = "mixed"

    else:
        verdict = "rejected"

    return SkepticVerdict(
        verdict=verdict,
        score=score,
        findings=tuple(findings),
    )
