from __future__ import annotations

from datetime import UTC, date, datetime

import clickhouse_connect

from laborlens.config import Settings
from laborlens.models import Observation, QcewObservation, SeriesMetadata


class ClickHouseStore:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.client = clickhouse_connect.get_client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            username=settings.clickhouse_user,
            password=(settings.clickhouse_password),
            database=(settings.clickhouse_database),
        )

    def ping(self) -> bool:
        result = self.client.command("SELECT 1")

        return result == 1

    def insert_series(
        self,
        series: SeriesMetadata,
    ) -> None:
        now = datetime.now(UTC)

        self.client.insert(
            "series",
            [
                [
                    series.series_id,
                    series.title,
                    series.frequency,
                    series.units,
                    series.seasonal_adjustment,
                    series.observation_start,
                    series.observation_end,
                    series.last_updated,
                    series.notes,
                    "FRED",
                    now,
                ]
            ],
            column_names=[
                "series_id",
                "title",
                "frequency",
                "units",
                "seasonal_adjustment",
                "observation_start",
                "observation_end",
                "last_updated",
                "notes",
                "source",
                "ingested_at",
            ],
        )

    def insert_observations(
        self,
        observations: list[Observation],
    ) -> int:
        if not observations:
            return 0

        now = datetime.now(UTC)

        rows = [
            [
                observation.series_id,
                observation.observation_date,
                observation.value,
                observation.realtime_start,
                observation.realtime_end,
                "FRED",
                now,
            ]
            for observation in observations
        ]

        self.client.insert(
            "observations",
            rows,
            column_names=[
                "series_id",
                "observation_date",
                "value",
                "realtime_start",
                "realtime_end",
                "source",
                "ingested_at",
            ],
        )

        return len(rows)

    def count_observations(
        self,
        series_id: str,
    ) -> int:
        result = self.client.query(
            """
            SELECT count()
            FROM observations
            WHERE series_id = %(series_id)s
            """,
            parameters={"series_id": (series_id.upper())},
        )

        return result.result_rows[0][0]

    def vintages_for_observation(
        self,
        series_id: str,
        observation_date: date,
    ) -> list[tuple]:
        result = self.client.query(
            """
            SELECT
                observation_date,
                value,
                realtime_start,
                realtime_end
            FROM observations
            WHERE
                series_id = %(series_id)s
                AND observation_date
                    = %(observation_date)s
            ORDER BY realtime_start
            """,
            parameters={
                "series_id": (series_id.upper()),
                "observation_date": (observation_date),
            },
        )

        return result.result_rows

    def provenance_for_window(
        self,
        series_id: str,
        start_date: date,
        end_date: date,
    ) -> list[tuple]:
        result = self.client.query(
            """
            SELECT
                observation_date,
                value,
                realtime_start,
                realtime_end
            FROM observations
            WHERE
                series_id = %(series_id)s
                AND observation_date >= %(start_date)s
                AND observation_date <= %(end_date)s
            ORDER BY
                observation_date,
                realtime_start
            """,
            parameters={
                "series_id": series_id.upper(),
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        return result.result_rows

    def latest_snapshot(
        self,
        series_id: str,
    ) -> list[tuple]:
        result = self.client.query(
            """
            SELECT
                observation_date,
                value,
                realtime_start,
                realtime_end
            FROM observations
            WHERE
                series_id = %(series_id)s
                AND ingested_at = (
                    SELECT max(ingested_at)
                    FROM observations
                    WHERE series_id = %(series_id)s
                )
            ORDER BY observation_date
            """,
            parameters={
                "series_id": series_id.upper(),
            },
        )

        return result.result_rows

    def latest_vintage_date(
        self,
        series_id: str,
    ) -> date | None:
        result = self.client.query(
            """
            SELECT max(realtime_start)
            FROM observations
            WHERE series_id = %(series_id)s
            """,
            parameters={
                "series_id": series_id.upper(),
            },
        )

        return result.result_rows[0][0]

    def information_series_on_date(
        self,
        series_ids: list[str],
        information_date: date,
    ) -> list[str]:
        if not series_ids:
            return []

        result = self.client.query(
            """
            SELECT DISTINCT
                series_id
            FROM observations
            WHERE
                series_id IN %(series_ids)s
                AND realtime_start
                    = %(information_date)s
            ORDER BY series_id
            """,
            parameters={
                "series_ids": tuple(series_id.upper() for series_id in series_ids),
                "information_date": information_date,
            },
        )

        return [row[0] for row in result.result_rows]

    def information_dates(
        self,
        series_ids: list[str],
        start_date: date,
        end_date: date,
    ) -> list[date]:
        if not series_ids:
            return []

        result = self.client.query(
            """
            SELECT DISTINCT
                realtime_start
            FROM observations
            WHERE
                series_id IN %(series_ids)s
                AND realtime_start
                    >= %(start_date)s
                AND realtime_start
                    <= %(end_date)s
            ORDER BY realtime_start
            """,
            parameters={
                "series_ids": tuple(series_id.upper() for series_id in series_ids),
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        return [row[0] for row in result.result_rows]

    def insert_qcew_rows(
        self,
        rows: list[tuple],
    ) -> int:
        """
        High-throughput QCEW ingestion path.

        Rows are already parsed and type-normalized by the
        streaming ingestion service, avoiding millions of
        Pydantic model allocations.
        """
        if not rows:
            return 0

        self.client.insert(
            "qcew_observations",
            rows,
            column_names=[
                "area_fips",
                "industry_code",
                "ownership_code",
                "aggregation_level_code",
                "size_code",
                "year",
                "quarter",
                "disclosure_code",
                "establishments",
                "month1_employment",
                "month2_employment",
                "month3_employment",
                "total_quarterly_wages",
                "taxable_quarterly_wages",
                "quarterly_contributions",
                "average_weekly_wage",
                "lq_disclosure_code",
                "establishment_location_quotient",
                "month1_employment_location_quotient",
                "month2_employment_location_quotient",
                "employment_location_quotient",
                "total_wage_location_quotient",
                "wage_location_quotient",
                "oty_disclosure_code",
                "oty_establishments_change",
                "oty_establishments_pct_change",
                "oty_month3_employment_change",
                "oty_month3_employment_pct_change",
                "oty_total_quarterly_wages_change",
                "oty_total_quarterly_wages_pct_change",
                "oty_average_weekly_wage_change",
                "oty_average_weekly_wage_pct_change",
                "source",
                "ingested_at",
            ],
        )

        return len(rows)

    def insert_qcew_observations(
        self,
        observations: list[QcewObservation],
    ) -> int:
        if not observations:
            return 0

        now = datetime.now(UTC)

        rows = [
            [
                observation.area_fips,
                observation.industry_code,
                observation.ownership_code,
                observation.year,
                observation.quarter,
                observation.establishments,
                observation.month1_employment,
                observation.month2_employment,
                observation.month3_employment,
                observation.total_quarterly_wages,
                observation.average_weekly_wage,
                observation.employment_location_quotient,
                observation.wage_location_quotient,
                observation.area_title,
                observation.industry_title,
                "BLS_QCEW",
                now,
            ]
            for observation in observations
        ]

        self.client.insert(
            "qcew_observations",
            rows,
            column_names=[
                "area_fips",
                "industry_code",
                "ownership_code",
                "year",
                "quarter",
                "establishments",
                "month1_employment",
                "month2_employment",
                "month3_employment",
                "total_quarterly_wages",
                "average_weekly_wage",
                "employment_location_quotient",
                "wage_location_quotient",
                "area_title",
                "industry_title",
                "source",
                "ingested_at",
            ],
        )

        return len(rows)

    def qcew_industry_employment(
        self,
        *,
        area_fips: str,
        industry_code: str,
        start_year: int,
        end_year: int,
    ) -> list[tuple]:
        result = self.client.query(
            """
            SELECT
                year,
                quarter,
                month3_employment,
                average_weekly_wage,
                employment_location_quotient
            FROM qcew_observations
            WHERE
                area_fips = %(area_fips)s
                AND industry_code = %(industry_code)s
                AND year >= %(start_year)s
                AND year <= %(end_year)s
            ORDER BY
                year,
                quarter
            """,
            parameters={
                "area_fips": area_fips,
                "industry_code": industry_code,
                "start_year": start_year,
                "end_year": end_year,
            },
        )

        return result.result_rows

    def qcew_compare_area_to_national(
        self,
        *,
        area_fips: str,
        year: int,
        quarter: int,
        ownership_code: int = 5,
        industry_level: int = 6,
        minimum_employment: int = 1_000,
        include_unclassified: bool = False,
    ) -> list[tuple]:
        if industry_level not in {
            2,
            3,
            4,
            5,
            6,
        }:
            raise ValueError("industry_level must be between 2 and 6")

        # QCEW aggregation levels differ by geography.
        #
        # National:
        # sector=14, 3-digit=15, ..., 6-digit=18
        #
        # Statewide:
        # sector=54, 3-digit=55, ..., 6-digit=58
        national_level = 12 + industry_level
        statewide_level = 52 + industry_level

        unclassified_clause = (
            "" if include_unclassified else "AND NOT startsWith(industry_code, '99')"
        )

        result = self.client.query(
            f"""
            WITH
            local AS
            (
                SELECT
                    industry_code,

                    argMax(
                        month3_employment,
                        ingested_at
                    ) AS employment,

                    argMax(
                        oty_month3_employment_pct_change,
                        ingested_at
                    ) AS yoy_growth,

                    argMax(
                        employment_location_quotient,
                        ingested_at
                    ) AS location_quotient

                FROM qcew_observations

                WHERE
                    year = %(year)s
                    AND quarter = %(quarter)s
                    AND area_fips = %(area_fips)s
                    AND ownership_code = %(ownership_code)s
                    AND aggregation_level_code
                        = %(statewide_level)s
                    AND disclosure_code = ''
                    {unclassified_clause}

                GROUP BY industry_code
            ),

            national AS
            (
                SELECT
                    industry_code,

                    argMax(
                        month3_employment,
                        ingested_at
                    ) AS employment,

                    argMax(
                        oty_month3_employment_pct_change,
                        ingested_at
                    ) AS yoy_growth

                FROM qcew_observations

                WHERE
                    year = %(year)s
                    AND quarter = %(quarter)s
                    AND area_fips = 'US000'
                    AND ownership_code = %(ownership_code)s
                    AND aggregation_level_code
                        = %(national_level)s
                    AND disclosure_code = ''
                    {unclassified_clause}

                GROUP BY industry_code
            )

            SELECT
                local.industry_code,
                industries.industry_title,
                local.employment,
                national.employment,
                local.yoy_growth,
                national.yoy_growth,

                local.yoy_growth
                    - national.yoy_growth
                    AS relative_growth,

                local.location_quotient

            FROM local

            INNER JOIN national
                USING industry_code

            LEFT JOIN
            (
                SELECT
                    industry_code,
                    argMax(
                        industry_title,
                        ingested_at
                    ) AS industry_title
                FROM qcew_industries
                WHERE naics_version = 2022
                GROUP BY industry_code
            ) AS industries
                USING industry_code

            WHERE
                local.employment
                    >= %(minimum_employment)s

            ORDER BY
                relative_growth ASC,
                local.employment DESC
            """,
            parameters={
                "area_fips": area_fips,
                "year": year,
                "quarter": quarter,
                "ownership_code": ownership_code,
                "statewide_level": statewide_level,
                "national_level": national_level,
                "minimum_employment": minimum_employment,
            },
        )

        return result.result_rows

    def qcew_area_title(
        self,
        area_fips: str,
    ) -> str | None:
        result = self.client.query(
            """
            SELECT
                argMax(
                    area_title,
                    ingested_at
                )
            FROM qcew_areas
            WHERE area_fips = %(area_fips)s
            """,
            parameters={
                "area_fips": area_fips,
            },
        )

        value = result.result_rows[0][0]

        return value or None

    def as_of(
        self,
        series_id: str,
        as_of_date: date,
    ) -> list[tuple]:
        result = self.client.query(
            """
            SELECT
                observation_date,

                argMax(
                    value,
                    tuple(
                        realtime_start,
                        ingested_at
                    )
                ) AS value,

                max(
                    realtime_start
                ) AS vintage_start,

                argMax(
                    realtime_end,
                    tuple(
                        realtime_start,
                        ingested_at
                    )
                ) AS vintage_end

            FROM observations

            WHERE
                series_id = %(series_id)s

                AND realtime_start
                    <= %(as_of_date)s

            GROUP BY
                observation_date

            ORDER BY
                observation_date
            """,
            parameters={
                "series_id": series_id.upper(),
                "as_of_date": as_of_date,
            },
        )

        return result.result_rows
