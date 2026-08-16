from __future__ import annotations

from datetime import date

from laborlens.data.fred import FredClient
from laborlens.storage.clickhouse import ClickHouseStore


class IngestionService:
    def __init__(
        self,
        fred: FredClient,
        store: ClickHouseStore,
    ) -> None:
        self.fred = fred
        self.store = store

    async def ingest_latest(
        self,
        series_id: str,
        *,
        observation_start: date | None = None,
        observation_end: date | None = None,
    ) -> int:
        series_id = series_id.upper()

        metadata = await self.fred.series(series_id)

        observations = await self.fred.observations(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
        )

        self.store.insert_series(metadata)

        return self.store.insert_observations(observations)

    async def ingest_vintages(
        self,
        series_id: str,
        *,
        vintage_dates: list[date],
        observation_start: date | None = None,
        observation_end: date | None = None,
    ) -> int:
        series_id = series_id.upper()

        metadata = await self.fred.series(series_id)

        observations = await self.fred.observations(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
            vintage_dates=vintage_dates,
        )

        self.store.insert_series(metadata)

        return self.store.insert_observations(observations)
