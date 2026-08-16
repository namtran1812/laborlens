from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from sklearn.svm import LinearSVC

from laborlens.api.planner import AskIntent
from laborlens.api.semantic_router import model

DEFAULT_ARTIFACT = Path(__file__).resolve().parents[2] / "models" / "intent_router.joblib"


@dataclass(frozen=True)
class LearnedRoute:
    intent: AskIntent
    causal_score: float
    causal_threshold: float
    top_score: float
    runner_up_score: float | None

    @property
    def causal(self) -> bool:
        return self.causal_score >= self.causal_threshold

    @property
    def margin(self) -> float | None:
        if self.runner_up_score is None:
            return None

        return self.top_score - self.runner_up_score


@dataclass(frozen=True)
class RouterArtifact:
    causal_classifier: LinearSVC
    causal_threshold: float
    intent_classifier: LinearSVC
    model_name: str
    training_examples: int


@lru_cache(maxsize=1)
def artifact() -> RouterArtifact:
    if not DEFAULT_ARTIFACT.exists():
        raise RuntimeError(
            "Learned intent-router artifact is missing. Run scripts/train_intent_router.py first."
        )

    payload = joblib.load(DEFAULT_ARTIFACT)

    return RouterArtifact(
        causal_classifier=payload["causal_classifier"],
        causal_threshold=float(payload["causal_threshold"]),
        intent_classifier=payload["intent_classifier"],
        model_name=str(payload["model_name"]),
        training_examples=int(payload["training_examples"]),
    )


def learned_route(
    question: str,
) -> LearnedRoute:
    encoder = model()

    embedding = encoder.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    router = artifact()

    causal_score = float(router.causal_classifier.decision_function(embedding)[0])

    if causal_score >= router.causal_threshold:
        return LearnedRoute(
            intent=AskIntent.CAUSAL_ATTRIBUTION,
            causal_score=causal_score,
            causal_threshold=(router.causal_threshold),
            top_score=causal_score,
            runner_up_score=None,
        )

    scores = router.intent_classifier.decision_function(embedding)[0]

    order = np.argsort(scores)[::-1]

    best_index = int(order[0])

    second_index = int(order[1])

    classes = router.intent_classifier.classes_

    return LearnedRoute(
        intent=AskIntent(str(classes[best_index])),
        causal_score=causal_score,
        causal_threshold=(router.causal_threshold),
        top_score=float(scores[best_index]),
        runner_up_score=float(scores[second_index]),
    )


def preload_router() -> None:
    """
    Load MiniLM and the trained classifiers eagerly.

    Production services can call this once during startup
    to avoid paying model initialization on the first query.
    """
    model()
    artifact()
