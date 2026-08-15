from datetime import date

import pytest

from laborlens.data.fred import (
    FredClient,
    FredError,
)


def test_requires_api_key() -> None:
    with pytest.raises(
        ValueError,
        match="FRED_API_KEY is required",
    ):
        FredClient("")


@pytest.mark.asyncio
async def test_series_parses_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FredClient("fake-key")

    async def fake_get(
        path: str,
        params: dict,
    ) -> dict:
        assert path == "series"
        assert params == {
            "series_id": "UNRATE",
        }

        return {
            "seriess": [
                {
                    "id": "UNRATE",
                    "title": "Unemployment Rate",
                    "frequency": "Monthly",
                    "units": "Percent",
                    "seasonal_adjustment": ("Seasonally Adjusted"),
                    "observation_start": ("1948-01-01"),
                    "observation_end": ("2026-07-01"),
                    "last_updated": ("2026-08-07 07:44:02-05"),
                    "notes": "Test notes.",
                }
            ]
        }

    monkeypatch.setattr(
        client,
        "_get",
        fake_get,
    )

    result = await client.series("unrate")

    assert result.series_id == "UNRATE"
    assert result.title == "Unemployment Rate"
    assert result.frequency == "Monthly"
    assert result.units == "Percent"
    assert result.observation_start == date(1948, 1, 1)


@pytest.mark.asyncio
async def test_observations_parse_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FredClient("fake-key")

    async def fake_get(
        path: str,
        params: dict,
    ) -> dict:
        assert path == "series/observations"

        assert params["series_id"] == "UNRATE"

        return {
            "observations": [
                {
                    "realtime_start": ("2026-08-01"),
                    "realtime_end": ("2026-08-31"),
                    "date": "2026-06-01",
                    "value": "4.1",
                },
                {
                    "realtime_start": ("2026-08-01"),
                    "realtime_end": ("2026-08-31"),
                    "date": "2026-07-01",
                    "value": ".",
                },
            ]
        }

    monkeypatch.setattr(
        client,
        "_get",
        fake_get,
    )

    rows = await client.observations("unrate")

    assert len(rows) == 2

    assert rows[0].series_id == "UNRATE"

    assert rows[0].observation_date == date(2026, 6, 1)

    assert rows[0].value == 4.1

    assert rows[1].value is None


@pytest.mark.asyncio
async def test_observation_date_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FredClient("fake-key")

    captured: dict = {}

    async def fake_get(
        path: str,
        params: dict,
    ) -> dict:
        captured.update(params)

        return {"observations": []}

    monkeypatch.setattr(
        client,
        "_get",
        fake_get,
    )

    await client.observations(
        "UNRATE",
        observation_start=date(
            2020,
            1,
            1,
        ),
        observation_end=date(
            2021,
            1,
            1,
        ),
    )

    assert captured["observation_start"] == "2020-01-01"

    assert captured["observation_end"] == "2021-01-01"


@pytest.mark.asyncio
async def test_vintage_dates_are_encoded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FredClient("fake-key")

    captured: dict = {}

    async def fake_get(
        path: str,
        params: dict,
    ) -> dict:
        captured.update(params)

        return {"observations": []}

    monkeypatch.setattr(
        client,
        "_get",
        fake_get,
    )

    await client.observations(
        "UNRATE",
        vintage_dates=[
            date(2024, 2, 1),
            date(2024, 3, 1),
            date(2024, 4, 1),
        ],
    )

    assert captured["vintage_dates"] == ("2024-02-01,2024-03-01,2024-04-01")


@pytest.mark.asyncio
async def test_unknown_series_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FredClient("fake-key")

    async def fake_get(
        path: str,
        params: dict,
    ) -> dict:
        return {"seriess": []}

    monkeypatch.setattr(
        client,
        "_get",
        fake_get,
    )

    with pytest.raises(
        FredError,
        match="series not found",
    ):
        await client.series("DOESNOTEXIST")
