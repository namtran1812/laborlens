from datetime import date
from unittest.mock import MagicMock

from laborlens.services.research_pipeline import ResearchPipeline


def test_rows_for_series_uses_latest_snapshot() -> None:
    store = MagicMock()

    store.latest_snapshot.return_value = [
        (
            date(2024, 1, 1),
            100.0,
            date(2026, 8, 1),
            date(2026, 8, 1),
        )
    ]

    pipeline = ResearchPipeline(store)

    rows = pipeline._rows_for_series(
        "PAYEMS",
        as_of_date=None,
    )

    assert len(rows) == 1

    store.latest_snapshot.assert_called_once_with("PAYEMS")

    store.as_of.assert_not_called()


def test_rows_for_series_uses_as_of_query() -> None:
    store = MagicMock()

    target = date(
        2024,
        9,
        1,
    )

    store.as_of.return_value = [
        (
            date(2024, 6, 1),
            100.0,
            date(2024, 7, 1),
            date(2024, 9, 5),
        )
    ]

    pipeline = ResearchPipeline(store)

    rows = pipeline._rows_for_series(
        "PAYEMS",
        as_of_date=target,
    )

    assert len(rows) == 1

    store.as_of.assert_called_once_with(
        "PAYEMS",
        target,
    )

    store.latest_snapshot.assert_not_called()
