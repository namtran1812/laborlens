from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from laborlens.models import Observation, SeriesMetadata


class FredError(RuntimeError):
    """Raised when a FRED request cannot be completed."""


class FredClient:
    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("FRED_API_KEY is required")

        self.api_key = api_key
        self.timeout = timeout

    async def _get(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        request_params = {
            **params,
            "api_key": self.api_key,
            "file_type": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.BASE_URL}/{path}",
                    params=request_params,
                )

                response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise FredError(f"FRED returned HTTP {exc.response.status_code} for {path}") from exc

        except httpx.RequestError as exc:
            raise FredError(f"Unable to reach FRED: {exc}") from exc

        payload = response.json()

        if "error_code" in payload:
            raise FredError(
                f"FRED error {payload['error_code']}: "
                f"{payload.get('error_message', 'unknown error')}"
            )

        return payload

    async def series(
        self,
        series_id: str,
    ) -> SeriesMetadata:
        series_id = series_id.upper()

        payload = await self._get(
            "series",
            {
                "series_id": series_id,
            },
        )

        rows = payload.get("seriess", [])

        if not rows:
            raise FredError(f"FRED series not found: {series_id}")

        row = rows[0]

        return SeriesMetadata(
            series_id=row["id"],
            title=row["title"],
            frequency=row["frequency"],
            units=row["units"],
            seasonal_adjustment=(row["seasonal_adjustment"]),
            observation_start=date.fromisoformat(row["observation_start"]),
            observation_end=date.fromisoformat(row["observation_end"]),
            last_updated=row["last_updated"],
            notes=row.get("notes", ""),
        )

    async def observations(
        self,
        series_id: str,
        *,
        observation_start: date | None = None,
        observation_end: date | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        vintage_dates: list[date] | None = None,
    ) -> list[Observation]:
        series_id = series_id.upper()

        params: dict[str, Any] = {
            "series_id": series_id,
        }

        if observation_start is not None:
            params["observation_start"] = observation_start.isoformat()

        if observation_end is not None:
            params["observation_end"] = observation_end.isoformat()

        if vintage_dates:
            params["vintage_dates"] = ",".join(vintage.isoformat() for vintage in vintage_dates)

        else:
            if realtime_start is not None:
                params["realtime_start"] = realtime_start.isoformat()

            if realtime_end is not None:
                params["realtime_end"] = realtime_end.isoformat()

        payload = await self._get(
            "series/observations",
            params,
        )

        observations: list[Observation] = []

        for row in payload.get(
            "observations",
            [],
        ):
            raw_value = row.get("value")

            value = (
                None
                if raw_value
                in {
                    None,
                    "",
                    ".",
                }
                else float(raw_value)
            )

            observations.append(
                Observation(
                    series_id=series_id,
                    observation_date=(date.fromisoformat(row["date"])),
                    value=value,
                    realtime_start=(date.fromisoformat(row["realtime_start"])),
                    realtime_end=(date.fromisoformat(row["realtime_end"])),
                )
            )

        return observations

    async def vintage_dates(
        self,
        series_id: str,
        *,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> list[date]:
        import httpx

        limit = 1000
        offset = 0
        result: list[date] = []

        async with httpx.AsyncClient(
            timeout=30.0,
        ) as client:
            while True:
                params = {
                    "series_id": series_id.upper(),
                    "api_key": self.api_key,
                    "file_type": "json",
                    "limit": limit,
                    "offset": offset,
                    "sort_order": "asc",
                }

                if realtime_start is not None:
                    params["realtime_start"] = realtime_start.isoformat()

                if realtime_end is not None:
                    params["realtime_end"] = realtime_end.isoformat()

                response = await client.get(
                    ("https://api.stlouisfed.org/fred/series/vintagedates"),
                    params=params,
                )

                response.raise_for_status()

                payload = response.json()

                values = payload.get(
                    "vintage_dates",
                    [],
                )

                result.extend(date.fromisoformat(value) for value in values)

                if len(values) < limit:
                    break

                offset += limit

        return result
