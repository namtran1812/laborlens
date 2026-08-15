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
