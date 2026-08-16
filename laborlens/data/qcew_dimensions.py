from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

import httpx

from laborlens.storage.clickhouse import ClickHouseStore


class QcewDimensionClient:
    INDUSTRY_URL = "https://data.bls.gov/cew/doc/titles/industry/industry_titles.csv"

    AREA_URL = "https://data.bls.gov/cew/doc/titles/area/area_titles.csv"

    def __init__(
        self,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.timeout = timeout

    async def _download(
        self,
        url: str,
    ) -> str:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        return response.text

    async def industry_rows(
        self,
    ) -> list[tuple[str, str]]:
        content = await self._download(self.INDUSTRY_URL)

        reader = csv.reader(io.StringIO(content))

        rows = []

        for row in reader:
            if len(row) < 2:
                continue

            code = row[0].strip().strip('"')
            title = row[1].strip().strip('"')

            if not code or code.lower() in {
                "industry_code",
                "industry code",
            }:
                continue

            rows.append(
                (
                    code,
                    title,
                )
            )

        return rows

    async def area_rows(
        self,
    ) -> list[tuple[str, str]]:
        content = await self._download(self.AREA_URL)

        reader = csv.reader(io.StringIO(content))

        rows = []

        for row in reader:
            if len(row) < 2:
                continue

            code = row[0].strip().strip('"')
            title = row[1].strip().strip('"')

            if not code or code.lower() in {
                "area_fips",
                "area code",
            }:
                continue

            rows.append(
                (
                    code,
                    title,
                )
            )

        return rows


class QcewDimensionService:
    def __init__(
        self,
        client: QcewDimensionClient,
        store: ClickHouseStore,
    ) -> None:
        self.client = client
        self.store = store

    async def ingest(
        self,
    ) -> tuple[int, int]:
        industries = await self.client.industry_rows()

        areas = await self.client.area_rows()

        now = datetime.now(UTC)

        industry_rows = [
            (
                code,
                title,
                2022,
                "BLS_QCEW",
                now,
            )
            for code, title in industries
        ]

        area_rows = [
            (
                code,
                title,
                "BLS_QCEW",
                now,
            )
            for code, title in areas
        ]

        self.store.client.insert(
            "qcew_industries",
            industry_rows,
            column_names=[
                "industry_code",
                "industry_title",
                "naics_version",
                "source",
                "ingested_at",
            ],
        )

        self.store.client.insert(
            "qcew_areas",
            area_rows,
            column_names=[
                "area_fips",
                "area_title",
                "source",
                "ingested_at",
            ],
        )

        return (
            len(industry_rows),
            len(area_rows),
        )
