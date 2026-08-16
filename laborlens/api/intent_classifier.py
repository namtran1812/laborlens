from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from sklearn.linear_model import (
    LogisticRegression,
)

from laborlens.api.planner import (
    AskIntent,
)
from laborlens.api.semantic_router import (
    model,
)


@dataclass(frozen=True)
class IntentPrediction:
    intent: AskIntent
    confidence: float
    runner_up: AskIntent
    runner_up_confidence: float

    @property
    def margin(self) -> float:
        return self.confidence - self.runner_up_confidence


@lru_cache(maxsize=1)
def training_examples() -> tuple[
    tuple[str, AskIntent],
    ...,
]:
    examples: list[tuple[str, AskIntent]] = []

    #
    # Development corpus.
    #
    from laborlens.evaluation.assistant_reliability import (
        planner_cases,
    )

    for case in planner_cases():
        examples.append(
            (
                case.question,
                case.intent,
            )
        )

    #
    # Former holdout V1.
    #
    from laborlens.evaluation.assistant_holdout import (
        holdout_cases,
    )

    for case in holdout_cases():
        examples.append(
            (
                case.question,
                case.intent,
            )
        )

    #
    # Former holdout V2.
    #
    from laborlens.evaluation.assistant_holdout_v2 import (
        CASES as V2_CASES,
    )

    for case in V2_CASES:
        examples.append(
            (
                case.question,
                case.intent,
            )
        )

    #
    # Former holdout V3.
    #
    from benchmarks.holdout_v3 import (
        CASES as V3_CASES,
    )

    for case in V3_CASES:
        examples.append(
            (
                case.question,
                case.intent,
            )
        )

    #
    # Deduplicate exact questions.
    #
    unique: dict[
        str,
        AskIntent,
    ] = {}

    for question, intent in examples:
        unique[question] = intent

    return tuple(unique.items())


@lru_cache(maxsize=1)
def classifier() -> tuple[
    LogisticRegression,
    tuple[AskIntent, ...],
]:
    examples = training_examples()

    questions = [question for question, _ in examples]

    labels = [intent.value for _, intent in examples]

    embeddings = model().encode(
        questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    clf.fit(
        embeddings,
        labels,
    )

    classes = tuple(AskIntent(value) for value in clf.classes_)

    return (
        clf,
        classes,
    )


def predict_intent(
    question: str,
) -> IntentPrediction:
    encoder = model()

    embedding = encoder.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    clf, classes = classifier()

    probabilities = clf.predict_proba(embedding)[0]

    order = np.argsort(probabilities)[::-1]

    best_index = int(order[0])

    second_index = int(order[1])

    return IntentPrediction(
        intent=classes[best_index],
        confidence=float(probabilities[best_index]),
        runner_up=classes[second_index],
        runner_up_confidence=float(probabilities[second_index]),
    )
