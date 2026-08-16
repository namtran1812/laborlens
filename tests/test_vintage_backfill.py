from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from laborlens.services.vintage_backfill import (
    VintageBackfillService,
)


@pytest.mark.asyncio
async def test_release_dates_uses_fred_vintages() -> None:
    fred = MagicMock()

    fred.vintage_dates = AsyncMock(
        return_value=[
            date(2024, 1, 5),
            date(2024, 2, 2),
        ]
    )

    store = MagicMock()

    service = VintageBackfillService(
        fred,
        store,
    )

    result = await service.release_dates(
        "PAYEMS",
        vintage_start=date(
            2024,
            1,
            1,
        ),
        vintage_end=date(
            2024,
            3,
            1,
        ),
    )

    assert result == [
        date(2024, 1, 5),
        date(2024, 2, 2),
    ]


@pytest.mark.asyncio
async def test_backfill_batches_vintage_dates() -> None:
    fred = MagicMock()

    fred.series = AsyncMock(return_value=MagicMock())

    fred.vintage_dates = AsyncMock(
        return_value=[
            date(2024, 1, 5),
            date(2024, 2, 2),
            date(2024, 3, 8),
        ]
    )

    fred.observations = AsyncMock(return_value=[])

    store = MagicMock()

    store.insert_observations.return_value = 0

    service = VintageBackfillService(
        fred,
        store,
    )

    vintage_count, inserted = await service.backfill_release_dates(
        "PAYEMS",
        vintage_start=date(
            2024,
            1,
            1,
        ),
        vintage_end=date(
            2024,
            4,
            1,
        ),
        observation_start=date(
            2023,
            1,
            1,
        ),
        observation_end=date(
            2024,
            3,
            1,
        ),
        batch_size=2,
    )

    assert vintage_count == 3
    assert inserted == 0

    assert fred.observations.await_count == 2


@pytest.mark.asyncio
async def test_invalid_batch_size() -> None:
    service = VintageBackfillService(
        MagicMock(),
        MagicMock(),
    )

    with pytest.raises(
        ValueError,
        match="batch_size",
    ):
        await service.backfill_release_dates(
            "PAYEMS",
            vintage_start=date(
                2024,
                1,
                1,
            ),
            vintage_end=date(
                2024,
                2,
                1,
            ),
            observation_start=date(
                2023,
                1,
                1,
            ),
            observation_end=date(
                2024,
                1,
                1,
            ),
            batch_size=0,
        )
