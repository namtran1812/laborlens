from __future__ import annotations

from laborlens.analysis.qcew import (
    QcewIndustryComparison,
    classify_comparison,
    weakening_score,
)
from laborlens.storage.clickhouse import ClickHouseStore


class QcewResearchService:
    def __init__(
        self,
        store: ClickHouseStore,
    ) -> None:
        self.store = store

    def compare_area_to_national(
        self,
        *,
        area_fips: str,
        year: int,
        quarter: int,
        minimum_employment: int = 1_000,
        industry_level: int = 6,
    ) -> list[QcewIndustryComparison]:
        rows = self.store.qcew_compare_area_to_national(
            area_fips=area_fips,
            year=year,
            quarter=quarter,
            minimum_employment=minimum_employment,
            industry_level=industry_level,
        )

        result: list[QcewIndustryComparison] = []

        for (
            industry_code,
            industry_title,
            local_employment,
            national_employment,
            local_growth,
            national_growth,
            relative_growth,
            location_quotient,
        ) in rows:
            comparison_type = classify_comparison(
                local_growth=local_growth,
                national_growth=national_growth,
            )

            result.append(
                QcewIndustryComparison(
                    industry_code=industry_code,
                    industry_title=(industry_title or industry_code),
                    local_employment=local_employment,
                    national_employment=national_employment,
                    local_yoy_growth=local_growth,
                    national_yoy_growth=national_growth,
                    relative_growth=relative_growth,
                    local_location_quotient=location_quotient,
                    comparison_type=comparison_type,
                    weakening_score=weakening_score(
                        local_growth=local_growth,
                        national_growth=national_growth,
                        location_quotient=location_quotient,
                    ),
                )
            )

        return sorted(
            result,
            key=lambda item: (
                item.weakening_score if item.weakening_score is not None else float("-inf")
            ),
            reverse=True,
        )
