from __future__ import annotations

from datetime import date

from laborlens.data.fred import FredClient
from laborlens.storage.clickhouse import ClickHouseStore


class VintageBackfillService:
    def __init__(
        self,
        fred: FredClient,
        store: ClickHouseStore,
    ) -> None:
        self.fred = fred
        self.store = store

    async def release_dates(
        self,
        series_id: str,
        *,
        vintage_start: date,
        vintage_end: date,
    ) -> list[date]:
        dates = await self.fred.vintage_dates(
            series_id,
            realtime_start=vintage_start,
            realtime_end=vintage_end,
        )

        return [value for value in dates if vintage_start <= value <= vintage_end]

    async def backfill_release_dates(
        self,
        series_id: str,
        *,
        vintage_start: date,
        vintage_end: date,
        observation_start: date,
        observation_end: date,
        batch_size: int = 250,
    ) -> tuple[int, int]:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")

        series_id = series_id.upper()

        metadata = await self.fred.series(series_id)

        vintage_dates = await self.release_dates(
            series_id,
            vintage_start=vintage_start,
            vintage_end=vintage_end,
        )

        self.store.insert_series(metadata)

        inserted = 0

        for offset in range(
            0,
            len(vintage_dates),
            batch_size,
        ):
            batch = vintage_dates[offset : offset + batch_size]

            rows = await self.fred.observations(
                series_id,
                observation_start=observation_start,
                observation_end=observation_end,
                vintage_dates=batch,
            )

            inserted += self.store.insert_observations(rows)

        return len(vintage_dates), inserted
