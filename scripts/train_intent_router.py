from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
)
from sklearn.svm import LinearSVC

from benchmarks.holdout_v3 import (
    CASES as V3_CASES,
)
from laborlens.api.semantic_router import (
    MODEL_NAME,
    model,
)
from laborlens.evaluation.assistant_holdout import (
    holdout_cases,
)
from laborlens.evaluation.assistant_holdout_v2 import (
    CASES as V2_CASES,
)
from laborlens.evaluation.assistant_reliability import (
    planner_cases,
)
from laborlens.evaluation.causal_training import (
    HARD_NEGATIVE_CAUSAL,
    POSITIVE_CAUSAL,
)

CAUSAL = "causal_attribution"

OUTPUT = Path("models/intent_router.joblib")


def make_causal_classifier() -> LinearSVC:
    return LinearSVC(
        class_weight={
            0: 1.0,
            1: 3.0,
        },
        C=1.0,
        random_state=42,
    )


def calibrated_threshold(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float, float]:
    causal_count = int(np.sum(y == 1))

    noncausal_count = int(np.sum(y == 0))

    folds = min(
        5,
        causal_count,
        noncausal_count,
    )

    splitter = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=42,
    )

    oof_scores = np.zeros(
        len(y),
        dtype=float,
    )

    for train_index, valid_index in splitter.split(
        x,
        y,
    ):
        clf = make_causal_classifier()

        clf.fit(
            x[train_index],
            y[train_index],
        )

        oof_scores[valid_index] = clf.decision_function(x[valid_index])

    candidates = sorted(
        np.unique(oof_scores),
        reverse=True,
    )

    for threshold in candidates:
        prediction = (oof_scores >= threshold).astype(int)

        recall = recall_score(
            y,
            prediction,
            zero_division=0,
        )

        if recall < 1.0:
            continue

        precision = precision_score(
            y,
            prediction,
            zero_division=0,
        )

        return (
            float(threshold),
            float(recall),
            float(precision),
        )

    raise RuntimeError("Unable to calibrate causal threshold")


def corpus() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []

    rows.extend(
        (
            case.question,
            case.intent.value,
        )
        for case in planner_cases()
    )

    rows.extend(
        (
            case.question,
            case.intent.value,
        )
        for case in holdout_cases()
    )

    rows.extend(
        (
            case.question,
            case.intent.value,
        )
        for case in V2_CASES
    )

    rows.extend(
        (
            case.question,
            case.intent.value,
        )
        for case in V3_CASES
    )

    #
    # Exact-question deduplication.
    #
    return list(dict(rows).items())


def main() -> None:
    rows = corpus()

    #
    # Hard causal examples are part of the binary
    # safety stage only.
    #
    causal_rows = list(rows)

    causal_rows.extend(
        (
            question,
            CAUSAL,
        )
        for question in POSITIVE_CAUSAL
    )

    causal_rows.extend(
        (
            question,
            "noncausal",
        )
        for question in HARD_NEGATIVE_CAUSAL
    )

    all_questions = list(dict.fromkeys(question for question, _ in causal_rows))

    encoder = model()

    embeddings = encoder.encode(
        all_questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    vectors = {question: embeddings[index] for index, question in enumerate(all_questions)}

    causal_x = np.stack([vectors[question] for question, _ in causal_rows])

    causal_y = np.array([1 if label == CAUSAL else 0 for _, label in causal_rows])

    (
        threshold,
        oof_recall,
        oof_precision,
    ) = calibrated_threshold(
        causal_x,
        causal_y,
    )

    causal_classifier = make_causal_classifier()

    causal_classifier.fit(
        causal_x,
        causal_y,
    )

    #
    # Stage 2 deliberately excludes causal examples.
    #
    noncausal_rows = [
        (
            question,
            label,
        )
        for question, label in rows
        if label != CAUSAL
    ]

    intent_x = np.stack([vectors[question] for question, _ in noncausal_rows])

    intent_y = np.array([label for _, label in noncausal_rows])

    intent_classifier = LinearSVC(
        C=1.0,
        class_weight="balanced",
        random_state=42,
    )

    intent_classifier.fit(
        intent_x,
        intent_y,
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        {
            "causal_classifier": (causal_classifier),
            "causal_threshold": (threshold),
            "intent_classifier": (intent_classifier),
            "model_name": (MODEL_NAME),
            "training_examples": (len(rows)),
            "causal_training_examples": (len(causal_rows)),
        },
        OUTPUT,
    )

    print(f"artifact={OUTPUT}")
    print(f"training_examples={len(rows)}")
    print(f"causal_training_examples={len(causal_rows)}")
    print(f"causal_threshold={threshold:.4f}")
    print(f"causal_oof_recall={oof_recall:.3f}")
    print(f"causal_oof_precision={oof_precision:.3f}")
    print("noncausal_classes=" + ",".join(intent_classifier.classes_))


if __name__ == "__main__":
    main()
