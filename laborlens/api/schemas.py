from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=800,
    )
    start_date: date
    as_of: date | None = None
    window: int = Field(
        default=24,
        ge=6,
        le=60,
    )
    min_confidence: float = Field(
        default=0.55,
        ge=0.0,
        le=1.0,
    )
    area: str | None = None
    industry_level: int = Field(
        default=6,
        ge=2,
        le=6,
    )
    context_limit: int = Field(
        default=5,
        ge=1,
        le=25,
    )


class AskResponse(BaseModel):
    answer: str
    mode: str
    model: str
    sources: list[str]
    caveat: str
