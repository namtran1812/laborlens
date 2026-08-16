from datetime import date

from pydantic import BaseModel


class SeriesMetadata(BaseModel):
    series_id: str
    title: str
    frequency: str
    units: str
    seasonal_adjustment: str
    observation_start: date
    observation_end: date
    last_updated: str
    notes: str = ""


class Observation(BaseModel):
    series_id: str
    observation_date: date
    value: float | None
    realtime_start: date
    realtime_end: date


class QcewObservation(BaseModel):
    area_fips: str
    industry_code: str
    ownership_code: int
    year: int
    quarter: int

    establishments: int | None = None
    month1_employment: int | None = None
    month2_employment: int | None = None
    month3_employment: int | None = None
    total_quarterly_wages: float | None = None
    average_weekly_wage: float | None = None

    employment_location_quotient: float | None = None
    wage_location_quotient: float | None = None

    area_title: str = ""
    industry_title: str = ""


class QcewIngestionResult(BaseModel):
    year: int
    quarter: int
    rows_received: int
    rows_valid: int
    rows_inserted: int
