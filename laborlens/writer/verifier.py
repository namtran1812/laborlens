from __future__ import annotations

import re
from dataclasses import dataclass

from laborlens.research.research_bundle import ResearchBundle

DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

NUMBER_PATTERN = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?%?")


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    unsupported_numbers: tuple[str, ...]
    unsupported_dates: tuple[str, ...]


def _allowed_dates(
    bundle: ResearchBundle,
) -> set[str]:
    allowed = {
        bundle.episode.start_date.isoformat(),
        bundle.episode.end_date.isoformat(),
        bundle.claim.observation_date.isoformat(),
    }

    for analog in bundle.historical_analogs:
        allowed.add(analog.start_date.isoformat())
        allowed.add(analog.end_date.isoformat())

    for item in bundle.provenance:
        allowed.add(item.observation_date.isoformat())
        allowed.add(item.realtime_start.isoformat())
        allowed.add(item.realtime_end.isoformat())

    return allowed


def _allowed_numbers(
    bundle: ResearchBundle,
) -> set[float]:
    allowed = {
        bundle.claim.confidence,
        bundle.evidence.dispersion,
        bundle.evidence.coverage,
        bundle.evidence.breadth,
        bundle.skeptic.score,
        bundle.mean_episode_score,
        bundle.peak_episode_score,
        bundle.historical_percentile,
        float(bundle.duration_months),
    }

    for item in bundle.evidence.supporting:
        allowed.add(item.contribution)

    for item in bundle.evidence.opposing:
        allowed.add(item.contribution)

    for analog in bundle.historical_analogs:
        allowed.add(analog.score)

        allowed.add(analog.confidence)

        allowed.add(float(analog.duration_months))

    for item in bundle.provenance:
        allowed.add(item.value)

    return allowed


def verify_article_numbers(
    article: str,
    bundle: ResearchBundle,
    *,
    tolerance: float = 0.015,
) -> VerificationResult:
    allowed_dates = _allowed_dates(bundle)

    dates = DATE_PATTERN.findall(article)

    unsupported_dates = tuple(value for value in dates if value not in allowed_dates)

    # Dates are verified separately, so remove
    # them before scanning ordinary numbers.
    numeric_text = DATE_PATTERN.sub(
        "",
        article,
    )

    allowed_numbers = _allowed_numbers(bundle)

    unsupported_numbers = []

    for token in NUMBER_PATTERN.findall(numeric_text):
        normalized = token.rstrip("%")

        try:
            value = float(normalized)
        except ValueError:
            continue

        candidates = (
            [
                value,
                value / 100.0,
            ]
            if token.endswith("%")
            else [value]
        )

        matched = any(
            any(abs(candidate - allowed_value) <= tolerance for allowed_value in allowed_numbers)
            for candidate in candidates
        )

        if not matched:
            unsupported_numbers.append(token)

    return VerificationResult(
        passed=(not unsupported_numbers and not unsupported_dates),
        unsupported_numbers=tuple(unsupported_numbers),
        unsupported_dates=(unsupported_dates),
    )
