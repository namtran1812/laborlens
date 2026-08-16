from __future__ import annotations

from dataclasses import dataclass

from laborlens.research.qcew_claims import (
    QcewClaim,
    generate_qcew_claims,
)
from laborlens.research.qcew_skeptic import (
    QcewSkepticResult,
    QcewSkepticVerdict,
    evaluate_qcew_claim,
)
from laborlens.services.qcew_research import (
    QcewResearchService,
)
from laborlens.storage.clickhouse import (
    ClickHouseStore,
)


@dataclass(frozen=True)
class ValidatedQcewClaim:
    claim: QcewClaim
    skeptic: QcewSkepticResult


class QcewClaimPipeline:
    def __init__(
        self,
        store: ClickHouseStore,
    ) -> None:
        self.store = store
        self.research = QcewResearchService(store)

    def discover(
        self,
        *,
        area_fips: str,
        year: int,
        quarter: int,
        industry_level: int = 6,
        minimum_employment: int = 10_000,
        minimum_relative_gap: float = 2.0,
        limit: int = 25,
    ) -> list[ValidatedQcewClaim]:
        area_title = self.store.qcew_area_title(area_fips) or area_fips

        comparisons = self.research.compare_area_to_national(
            area_fips=area_fips,
            year=year,
            quarter=quarter,
            minimum_employment=(minimum_employment),
            industry_level=(industry_level),
        )

        claims = generate_qcew_claims(
            comparisons,
            area_fips=area_fips,
            area_title=area_title,
            year=year,
            quarter=quarter,
            minimum_employment=(minimum_employment),
            minimum_relative_gap=(minimum_relative_gap),
        )

        validated = []

        for claim in claims:
            skeptic = evaluate_qcew_claim(claim)

            if skeptic.verdict == QcewSkepticVerdict.REJECTED:
                continue

            validated.append(
                ValidatedQcewClaim(
                    claim=claim,
                    skeptic=skeptic,
                )
            )

        return validated[:limit]
