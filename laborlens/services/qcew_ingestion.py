from __future__ import annotations

import csv
import io
import tempfile
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from laborlens.data.qcew import QcewClient, QcewError
from laborlens.models import QcewIngestionResult
from laborlens.storage.clickhouse import ClickHouseStore


class QcewIngestionService:
    def __init__(
        self,
        qcew: QcewClient,
        store: ClickHouseStore,
    ) -> None:
        self.qcew = qcew
        self.store = store

    @staticmethod
    def _int(
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return int(float(value))

    @staticmethod
    def _float(
        value: str | None,
    ) -> float | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return float(value)

    @classmethod
    def _row_tuple(
        cls,
        row: dict[str, str],
        ingested_at: datetime,
    ) -> tuple:
        return (
            row["area_fips"].strip(),
            row["industry_code"].strip(),
            int(row["own_code"]),
            int(row["agglvl_code"]),
            int(row["size_code"]),
            int(row["year"]),
            int(row["qtr"]),
            row.get(
                "disclosure_code",
                "",
            ).strip(),
            cls._int(row.get("qtrly_estabs")),
            cls._int(row.get("month1_emplvl")),
            cls._int(row.get("month2_emplvl")),
            cls._int(row.get("month3_emplvl")),
            cls._float(row.get("total_qtrly_wages")),
            cls._float(row.get("taxable_qtrly_wages")),
            cls._float(row.get("qtrly_contributions")),
            cls._float(row.get("avg_wkly_wage")),
            row.get(
                "lq_disclosure_code",
                "",
            ).strip(),
            cls._float(row.get("lq_qtrly_estabs")),
            cls._float(row.get("lq_month1_emplvl")),
            cls._float(row.get("lq_month2_emplvl")),
            cls._float(row.get("lq_month3_emplvl")),
            cls._float(row.get("lq_total_qtrly_wages")),
            cls._float(row.get("lq_avg_wkly_wage")),
            row.get(
                "oty_disclosure_code",
                "",
            ).strip(),
            cls._int(row.get("oty_qtrly_estabs_chg")),
            cls._float(row.get("oty_qtrly_estabs_pct_chg")),
            cls._int(row.get("oty_month3_emplvl_chg")),
            cls._float(row.get("oty_month3_emplvl_pct_chg")),
            cls._int(row.get("oty_total_qtrly_wages_chg")),
            cls._float(row.get("oty_total_qtrly_wages_pct_chg")),
            cls._int(row.get("oty_avg_wkly_wage_chg")),
            cls._float(row.get("oty_avg_wkly_wage_pct_chg")),
            "BLS_QCEW",
            ingested_at,
        )

    async def ingest_quarter(
        self,
        year: int,
        quarter: int,
        *,
        batch_size: int = 25_000,
    ) -> QcewIngestionResult:
        if quarter not in {
            1,
            2,
            3,
            4,
        }:
            raise ValueError("quarter must be between 1 and 4")

        if batch_size < 1:
            raise ValueError("batch_size must be positive")

        started = time.perf_counter()

        rows_scanned = 0
        rows_matching = 0
        rows_inserted = 0
        batches_inserted = 0

        with tempfile.TemporaryDirectory(prefix="laborlens-qcew-") as temp_directory:
            archive_path = Path(temp_directory) / f"{year}_qtrly_singlefile.zip"

            archive_bytes = await self.qcew.download_year_archive_to(
                year,
                archive_path,
            )

            try:
                with zipfile.ZipFile(archive_path) as archive:
                    csv_members = [
                        name for name in archive.namelist() if name.lower().endswith(".csv")
                    ]

                    if len(csv_members) != 1:
                        raise QcewError(
                            "Expected exactly one CSV in "
                            "QCEW singlefile archive; "
                            f"found {len(csv_members)}"
                        )

                    member = csv_members[0]
                    info = archive.getinfo(member)

                    with (
                        archive.open(member) as raw,
                        io.TextIOWrapper(
                            raw,
                            encoding="utf-8-sig",
                            newline="",
                        ) as stream,
                    ):
                        reader = csv.DictReader(stream)

                        batch: list[tuple] = []

                        ingested_at = datetime.now(UTC)

                        for row in reader:
                            rows_scanned += 1

                            if int(row["qtr"]) != quarter:
                                continue

                            rows_matching += 1

                            batch.append(
                                self._row_tuple(
                                    row,
                                    ingested_at,
                                )
                            )

                            if len(batch) >= batch_size:
                                rows_inserted += self.store.insert_qcew_rows(batch)

                                batches_inserted += 1
                                batch.clear()

                        if batch:
                            rows_inserted += self.store.insert_qcew_rows(batch)

                            batches_inserted += 1

            except zipfile.BadZipFile as exc:
                raise QcewError("QCEW response is not a valid ZIP archive") from exc

        elapsed = time.perf_counter() - started

        rows_per_second = rows_scanned / elapsed if elapsed else 0.0

        print(f"archive_bytes={archive_bytes}")

        print(f"uncompressed_bytes={info.file_size}")

        print(f"rows_scanned={rows_scanned}")

        print(f"rows_matching_quarter={rows_matching}")

        print(f"batches_inserted={batches_inserted}")

        print(f"elapsed_seconds={elapsed:.3f}")

        print(f"rows_per_second={rows_per_second:.1f}")

        return QcewIngestionResult(
            year=year,
            quarter=quarter,
            rows_received=rows_scanned,
            rows_valid=rows_matching,
            rows_inserted=rows_inserted,
        )
