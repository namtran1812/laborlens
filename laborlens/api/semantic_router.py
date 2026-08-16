from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from sentence_transformers import (
    SentenceTransformer,
)

from laborlens.api.planner import AskIntent

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


INTENT_EXAMPLES: dict[
    AskIntent,
    tuple[str, ...],
] = {
    AskIntent.MACRO_EVIDENCE: (
        ("Which macro indicators contributed most to the episode?"),
        ("What labor data series provided the strongest evidence?"),
        ("Rank the signals supporting the regime classification."),
        ("Which economic indicators were most important to the result?"),
        ("What evidence sits underneath the macro classification?"),
        ("Which labor measures carried the broad contraction signal?"),
        ("Which data series had the greatest influence on the classification?"),
        ("Which series contributed most strongly to the final classification result?"),
    ),
    AskIntent.INDUSTRY_WEAKNESS: (
        ("Which industries in this geography underperformed their national peers?"),
        ("Where did local employment lag the national industry?"),
        ("Show industries with relative employment weakness."),
        ("Which sectors contracted or performed worse than the national benchmark?"),
        ("Where is this geography losing ground relative to the country?"),
        ("Identify weak local industries compared with US counterparts."),
    ),
    AskIntent.INDUSTRY_STRENGTH: (
        ("Which industries in this geography outperformed their national peers?"),
        ("Where did local employment hold up better than the national industry?"),
        ("Show industries with relative employment strength."),
        ("Which sectors were resilient or performed better than the US?"),
        ("Where is this geography gaining ground against national trends?"),
        ("Identify strong local industries compared with national counterparts."),
    ),
    AskIntent.INDUSTRY_CONTEXT: (
        ("Give me an industry-level breakdown for this geography."),
        ("Show the cross-sectional sector context."),
        ("What does QCEW show across local industries?"),
        ("Break the geographic employment picture down by sector."),
        ("Compare local industries with their national counterparts."),
        ("What industry context complements the national macro signal?"),
    ),
    AskIntent.POINT_IN_TIME: (
        ("How does the system prevent future information from leaking into history?"),
        ("Was this data actually available at the historical as-of date?"),
        ("How are revisions and vintage data handled?"),
        ("How does the analysis avoid hindsight and look-ahead bias?"),
        ("Which release was available at that historical point in time?"),
        ("How are publication dates enforced in historical analysis?"),
    ),
    AskIntent.METHODOLOGY: (
        ("How does LaborLens transform raw data into an episode?"),
        ("Explain the methodology used to detect labor-market regimes."),
        ("How are indicators normalized, combined, smoothed, and clustered?"),
        ("What is the analytical workflow behind the classification?"),
        ("How does the research engine validate claims?"),
        ("Explain the procedure from observations to a validated episode."),
    ),
    AskIntent.EPISODE_SUMMARY: (
        ("Summarize what LaborLens found in this episode."),
        ("Give me the high-level result of the labor-market episode."),
        ("What happened in this episode?"),
        ("Give me the short version of what the system detected."),
        ("What is the main takeaway from this period?"),
        ("Give me an overview of the episode."),
    ),
    AskIntent.CAUSAL_ATTRIBUTION: (
        ("Did this external factor cause the labor-market change?"),
        ("Can the observed contraction be attributed to this event?"),
        ("Was this policy responsible for the employment weakness?"),
        ("Does the evidence prove this factor explains the result?"),
        ("Was this the underlying driver of the observed change?"),
        ("Can we blame this economic outcome on that factor?"),
    ),
}


@dataclass(frozen=True)
class SemanticRoute:
    intent: AskIntent
    score: float
    runner_up_intent: AskIntent
    runner_up_score: float

    @property
    def margin(self) -> float:
        return self.score - self.runner_up_score


@lru_cache(maxsize=1)
def model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def intent_examples() -> dict[
    AskIntent,
    np.ndarray,
]:
    encoder = model()

    encoded: dict[
        AskIntent,
        np.ndarray,
    ] = {}

    for intent, examples in INTENT_EXAMPLES.items():
        encoded[intent] = encoder.encode(
            list(examples),
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    return encoded


def semantic_route(
    question: str,
) -> SemanticRoute:
    encoder = model()

    query = encoder.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )[0]

    scores: list[tuple[AskIntent, float]] = []

    for intent, examples in intent_examples().items():
        similarities = examples @ query

        #
        # Use the strongest semantic exemplar rather
        # than averaging distinct concepts into one
        # potentially blurry centroid.
        #
        score = float(np.max(similarities))

        scores.append(
            (
                intent,
                score,
            )
        )

    scores.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    best_intent, best_score = scores[0]

    runner_intent, runner_score = scores[1]

    return SemanticRoute(
        intent=best_intent,
        score=best_score,
        runner_up_intent=runner_intent,
        runner_up_score=runner_score,
    )
