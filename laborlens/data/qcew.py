from __future__ import annotations

import csv
import io
from pathlib import Path

import httpx

from laborlens.models import QcewObservation


class QcewError(RuntimeError):
    """Raised when a QCEW request cannot be completed."""


class QcewClient:
    """
    Client for public BLS Quarterly Census of Employment and Wages data.

    QCEW bulk files require no API key.
    """

    BASE_URL = "https://data.bls.gov/cew/data/files"

    def __init__(
        self,
        *,
        timeout: float = 120.0,
    ) -> None:
        self.timeout = timeout

    @staticmethod
    def _optional_int(
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return int(float(value))

    @staticmethod
    def _optional_float(
        value: str | None,
    ) -> float | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return float(value)

    @classmethod
    def quarterly_url(
        cls,
        year: int,
        quarter: int,
    ) -> str:
        if quarter not in {1, 2, 3, 4}:
            raise ValueError("quarter must be between 1 and 4")

        # BLS publishes one quarterly
        # single-file archive per year.
        # Individual records inside the archive
        # contain their own quarter field.
        return f"{cls.BASE_URL}/{year}/csv/{year}_qtrly_singlefile.zip"

    async def download_year_archive_to(
        self,
        year: int,
        destination: Path,
    ) -> int:
        """
        Stream the official yearly QCEW quarterly archive
        directly to disk.

        Returns the number of bytes downloaded.
        """
        url = self.quarterly_url(
            year,
            1,
        )

        downloaded = 0

        try:
            async with (
                httpx.AsyncClient(
                    timeout=None,
                    follow_redirects=True,
                ) as client,
                client.stream(
                    "GET",
                    url,
                ) as response,
            ):
                response.raise_for_status()

                with destination.open("wb") as output:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        output.write(chunk)
                        downloaded += len(chunk)

        except httpx.HTTPStatusError as exc:
            raise QcewError(f"QCEW returned HTTP {exc.response.status_code} for {url}") from exc

        except httpx.RequestError as exc:
            raise QcewError(f"Unable to reach QCEW: {exc}") from exc

        return downloaded

    async def download_quarter(
        self,
        year: int,
        quarter: int,
    ) -> bytes:
        url = self.quarterly_url(
            year,
            quarter,
        )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise QcewError(f"QCEW returned HTTP {exc.response.status_code} for {url}") from exc

        except httpx.RequestError as exc:
            raise QcewError(f"Unable to reach QCEW: {exc}") from exc

        return response.content

    @classmethod
    def parse_csv(
        cls,
        content: str,
    ) -> list[QcewObservation]:
        reader = csv.DictReader(
            io.StringIO(content),
        )

        observations: list[QcewObservation] = []

        for row in reader:
            observations.append(
                QcewObservation(
                    area_fips=row["area_fips"].strip(),
                    industry_code=row["industry_code"].strip(),
                    ownership_code=int(row["own_code"]),
                    year=int(row["year"]),
                    quarter=int(row["qtr"]),
                    establishments=cls._optional_int(row.get("qtrly_estabs")),
                    month1_employment=cls._optional_int(row.get("month1_emplvl")),
                    month2_employment=cls._optional_int(row.get("month2_emplvl")),
                    month3_employment=cls._optional_int(row.get("month3_emplvl")),
                    total_quarterly_wages=cls._optional_float(row.get("total_qtrly_wages")),
                    average_weekly_wage=cls._optional_float(row.get("avg_wkly_wage")),
                    employment_location_quotient=cls._optional_float(row.get("lq_month3_emplvl")),
                    wage_location_quotient=cls._optional_float(row.get("lq_avg_wkly_wage")),
                    area_title=row.get(
                        "area_title",
                        "",
                    ).strip(),
                    industry_title=row.get(
                        "industry_title",
                        "",
                    ).strip(),
                )
            )

        return observations
