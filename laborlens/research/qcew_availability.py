from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class QcewRelease:
    reference_year: int
    reference_quarter: int
    full_data_release_date: date


# Official BLS QCEW full-data release dates.
#
# These dates describe when the detailed QCEW dataset used by
# LaborLens became publicly available, not merely when the
# high-level County Employment and Wages news release appeared.
QCEW_RELEASES: tuple[QcewRelease, ...] = (
    QcewRelease(
        reference_year=2022,
        reference_quarter=1,
        full_data_release_date=date(2022, 9, 7),
    ),
    QcewRelease(
        reference_year=2022,
        reference_quarter=2,
        full_data_release_date=date(2022, 12, 6),
    ),
    QcewRelease(
        reference_year=2022,
        reference_quarter=3,
        full_data_release_date=date(2023, 3, 8),
    ),
    QcewRelease(
        reference_year=2022,
        reference_quarter=4,
        full_data_release_date=date(2023, 6, 7),
    ),
    QcewRelease(
        reference_year=2023,
        reference_quarter=1,
        full_data_release_date=date(2023, 9, 6),
    ),
    QcewRelease(
        reference_year=2023,
        reference_quarter=2,
        full_data_release_date=date(2023, 12, 7),
    ),
    QcewRelease(
        reference_year=2023,
        reference_quarter=3,
        full_data_release_date=date(2024, 3, 6),
    ),
    QcewRelease(
        reference_year=2023,
        reference_quarter=4,
        full_data_release_date=date(2024, 6, 5),
    ),
    QcewRelease(
        reference_year=2024,
        reference_quarter=1,
        full_data_release_date=date(2024, 9, 4),
    ),
    QcewRelease(
        reference_year=2024,
        reference_quarter=2,
        full_data_release_date=date(2024, 12, 5),
    ),
    QcewRelease(
        reference_year=2024,
        reference_quarter=3,
        full_data_release_date=date(2025, 3, 5),
    ),
    QcewRelease(
        reference_year=2024,
        reference_quarter=4,
        full_data_release_date=date(2025, 6, 4),
    ),
)


def available_qcew_release(
    as_of_date: date,
) -> QcewRelease | None:
    available = [
        release for release in QCEW_RELEASES if (release.full_data_release_date <= as_of_date)
    ]

    if not available:
        return None

    return max(
        available,
        key=lambda release: (
            release.full_data_release_date,
            release.reference_year,
            release.reference_quarter,
        ),
    )


def qcew_release_for_period(
    year: int,
    quarter: int,
) -> QcewRelease | None:
    for release in QCEW_RELEASES:
        if release.reference_year == year and release.reference_quarter == quarter:
            return release

    return None
