from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from laborlens.services.qcew_claim_pipeline import (
    QcewClaimPipeline,
)
from laborlens.storage.clickhouse import ClickHouseStore


@dataclass(frozen=True)
class CrossSectionalClaim:
    claim_type: str

    industry_code: str
    industry_title: str

    local_employment: int

    local_yoy_growth: float
    national_yoy_growth: float
    relative_gap: float

    location_quotient: float | None

    strength: float

    skeptic_verdict: str
    skeptic_score: float

    headline: str
    evidence_text: str


@dataclass(frozen=True)
class CrossSectionalContext:
    area_fips: str
    area_title: str

    year: int
    quarter: int

    industry_level: int

    context_mode: str
    data_release_date: date | None
    requested_as_of_date: date | None

    claims: tuple[CrossSectionalClaim, ...]


def build_qcew_context(
    store: ClickHouseStore,
    *,
    area_fips: str,
    year: int,
    quarter: int,
    industry_level: int = 6,
    minimum_employment: int = 10_000,
    minimum_relative_gap: float = 2.0,
    limit: int = 5,
    context_mode: str = "retrospective",
    data_release_date: date | None = None,
    requested_as_of_date: date | None = None,
) -> CrossSectionalContext:
    pipeline = QcewClaimPipeline(store)

    validated = pipeline.discover(
        area_fips=area_fips,
        year=year,
        quarter=quarter,
        industry_level=industry_level,
        minimum_employment=minimum_employment,
        minimum_relative_gap=minimum_relative_gap,
        limit=limit,
    )

    area_title = store.qcew_area_title(area_fips) or area_fips

    claims = tuple(
        CrossSectionalClaim(
            claim_type=str(item.claim.claim_type),
            industry_code=(item.claim.industry_code),
            industry_title=(item.claim.industry_title),
            local_employment=(item.claim.local_employment),
            local_yoy_growth=(item.claim.local_yoy_growth),
            national_yoy_growth=(item.claim.national_yoy_growth),
            relative_gap=(item.claim.relative_gap),
            location_quotient=(item.claim.location_quotient),
            strength=(item.claim.strength),
            skeptic_verdict=str(item.skeptic.verdict),
            skeptic_score=(item.skeptic.score),
            headline=(item.claim.headline),
            evidence_text=(item.claim.evidence_text),
        )
        for item in validated
    )

    return CrossSectionalContext(
        area_fips=area_fips,
        area_title=area_title,
        year=year,
        quarter=quarter,
        industry_level=industry_level,
        context_mode=context_mode,
        data_release_date=data_release_date,
        requested_as_of_date=requested_as_of_date,
        claims=claims,
    )
