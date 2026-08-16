from __future__ import annotations

from datetime import UTC, date, datetime

import clickhouse_connect

from laborlens.config import Settings
from laborlens.models import Observation, SeriesMetadata


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
                    realtime_start
                ) AS value,

                max(
                    realtime_start
                ) AS vintage_start,

                argMax(
                    realtime_end,
                    realtime_start
                ) AS vintage_end

            FROM observations

            WHERE
                series_id = %(series_id)s

                AND realtime_start
                    <= %(as_of_date)s

                AND realtime_end
                    >= %(as_of_date)s

            GROUP BY
                observation_date

            ORDER BY
                observation_date
            """,
            parameters={
                "series_id": (series_id.upper()),
                "as_of_date": (as_of_date),
            },
        )

        return result.result_rows
