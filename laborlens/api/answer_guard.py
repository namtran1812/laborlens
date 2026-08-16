from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerGuardResult:
    valid: bool
    violations: tuple[str, ...]


CAUSAL_PATTERNS = (
    r"\bcaused by\b",
    r"\bdriven by\b",
    r"\bdue to\b",
    r"\bbecause of\b",
    r"\bresulted from\b",
    r"\binfluenced by\b",
    r"\bled to\b",
    r"\bresponsible for\b",
)

# Negative causal assertions are unsupported too.
CAUSAL_NEGATION_PATTERNS = (
    r"\bwas not the reason\b",
    r"\bwere not the reason\b",
    r"\bdid not cause\b",
    r"\bwas not caused by\b",
    r"\bwere not caused by\b",
)

MACRO_SERIES = (
    "PAYEMS",
    "UNRATE",
    "ICSA",
    "JTSHIR",
    "JTSJOL",
)

RAW_CHANGE_WORDS = (
    "declined",
    "fell",
    "dropped",
    "decreased",
    "rose",
    "increased",
    "grew",
    "was negative",
    "were negative",
    "was positive",
    "were positive",
)


def validate_ai_answer(
    answer: str,
) -> AnswerGuardResult:
    normalized = answer.lower()
    violations: list[str] = []

    for pattern in (
        *CAUSAL_PATTERNS,
        *CAUSAL_NEGATION_PATTERNS,
    ):
        if re.search(
            pattern,
            normalized,
        ):
            violations.append("unsupported causal assertion: " + pattern)

    for series in MACRO_SERIES:
        lower_series = series.lower()

        # Look around the series name for natural-unit
        # change language. The verified bundle contains
        # standardized contributions, not those raw facts.
        for match in re.finditer(
            re.escape(lower_series),
            normalized,
        ):
            start = max(
                0,
                match.start() - 80,
            )
            end = min(
                len(normalized),
                match.end() + 80,
            )
            window = normalized[start:end]

            if any(phrase in window for phrase in RAW_CHANGE_WORDS):
                violations.append(
                    f"{series} standardized contribution "
                    "may have been represented as a raw "
                    "series change"
                )
                break

    return AnswerGuardResult(
        valid=not violations,
        violations=tuple(dict.fromkeys(violations)),
    )
