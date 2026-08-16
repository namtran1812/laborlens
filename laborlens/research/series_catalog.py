from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesDefinition:
    series_id: str
    name: str
    description: str


SERIES_CATALOG = {
    "PAYEMS": SeriesDefinition(
        series_id="PAYEMS",
        name="Total nonfarm payroll employment",
        description=("Seasonally adjusted total nonfarm payroll employment."),
    ),
    "ICSA": SeriesDefinition(
        series_id="ICSA",
        name="Initial unemployment claims",
        description=("Seasonally adjusted weekly initial claims for unemployment insurance."),
    ),
    "UNRATE": SeriesDefinition(
        series_id="UNRATE",
        name="Unemployment rate",
        description=("Seasonally adjusted unemployment rate as a percentage of the labor force."),
    ),
    "JTSHIR": SeriesDefinition(
        series_id="JTSHIR",
        name="Hires rate",
        description=("Job Openings and Labor Turnover Survey hires rate."),
    ),
    "JTSJOL": SeriesDefinition(
        series_id="JTSJOL",
        name="Job openings level",
        description=("Job Openings and Labor Turnover Survey job openings."),
    ),
}


def series_name(
    series_id: str,
) -> str:
    definition = SERIES_CATALOG.get(series_id)

    if definition is None:
        return series_id

    return definition.name
