from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from laborlens.research.qcew_claims import (
    QcewClaim,
    QcewClaimType,
)


class QcewSkepticVerdict(StrEnum):
    SUPPORTED = "supported"
    WEAK = "weak"
    REJECTED = "rejected"


@dataclass(frozen=True)
class QcewSkepticResult:
    verdict: QcewSkepticVerdict
    score: float
    reasons: tuple[str, ...]


def evaluate_qcew_claim(
    claim: QcewClaim,
) -> QcewSkepticResult:
    reasons: list[str] = []
    score = 1.0

    if claim.local_employment < 10_000:
        score -= 0.35
        reasons.append("local employment below 10,000")

    if abs(claim.relative_gap) < 2.0:
        score -= 0.35
        reasons.append("relative gap below 2 percentage points")

    if claim.claim_type == QcewClaimType.LOCAL_CONTRACTION and claim.local_yoy_growth >= 0:
        return QcewSkepticResult(
            verdict=QcewSkepticVerdict.REJECTED,
            score=0.0,
            reasons=("contraction claim has non-negative local growth",),
        )

    if claim.claim_type == QcewClaimType.RELATIVE_UNDERPERFORMANCE and claim.local_yoy_growth < 0:
        score -= 0.25
        reasons.append("negative local growth should be classified as contraction")

    if claim.location_quotient is not None and claim.location_quotient < 0.5:
        score -= 0.10
        reasons.append("industry has low local concentration")

    score = max(
        0.0,
        min(1.0, score),
    )

    if score >= 0.75:
        verdict = QcewSkepticVerdict.SUPPORTED
    elif score >= 0.50:
        verdict = QcewSkepticVerdict.WEAK
    else:
        verdict = QcewSkepticVerdict.REJECTED

    return QcewSkepticResult(
        verdict=verdict,
        score=score,
        reasons=tuple(reasons),
    )
