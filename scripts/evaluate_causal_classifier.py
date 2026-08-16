from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import LinearSVC

from benchmarks.holdout_v3 import CASES as V3_CASES
from laborlens.api.semantic_router import model
from laborlens.evaluation.assistant_holdout import holdout_cases
from laborlens.evaluation.assistant_holdout_v2 import CASES as V2_CASES
from laborlens.evaluation.assistant_reliability import planner_cases
from laborlens.evaluation.causal_training import (
    HARD_NEGATIVE_CAUSAL,
    POSITIVE_CAUSAL,
)

CAUSAL = "causal_attribution"


def corpora():
    return {
        "dev": [(case.question, case.intent.value) for case in planner_cases()],
        "v1": [(case.question, case.intent.value) for case in holdout_cases()],
        "v2": [(case.question, case.intent.value) for case in V2_CASES],
        "v3": [(case.question, case.intent.value) for case in V3_CASES],
    }


def make_classifier():
    return LinearSVC(
        class_weight={
            0: 1.0,
            1: 3.0,
        },
        C=1.0,
        random_state=42,
    )


def calibrate_threshold(x, y):
    splitter = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scores = np.zeros(len(y))

    for train_idx, valid_idx in splitter.split(x, y):
        clf = make_classifier()
        clf.fit(
            x[train_idx],
            y[train_idx],
        )

        scores[valid_idx] = clf.decision_function(x[valid_idx])

    candidates = sorted(
        np.unique(scores),
        reverse=True,
    )

    for threshold in candidates:
        prediction = (scores >= threshold).astype(int)

        recall = recall_score(
            y,
            prediction,
            zero_division=0,
        )

        if recall == 1.0:
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

    return (
        float(np.min(scores) - 1e-6),
        1.0,
        0.0,
    )


def main():
    data = corpora()

    all_questions = list(
        dict.fromkeys(
            [question for rows in data.values() for question, _ in rows]
            + list(POSITIVE_CAUSAL)
            + list(HARD_NEGATIVE_CAUSAL)
        )
    )

    embeddings = model().encode(
        all_questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    vectors = {question: embeddings[index] for index, question in enumerate(all_questions)}

    for held_out in data:
        train_rows = [row for name, rows in data.items() if name != held_out for row in rows]

        # Add hard causal training examples.
        train_rows += [(question, CAUSAL) for question in POSITIVE_CAUSAL]

        train_rows += [(question, "noncausal") for question in HARD_NEGATIVE_CAUSAL]

        test_rows = data[held_out]

        train_x = np.stack([vectors[question] for question, _ in train_rows])

        train_y = np.array([1 if label == CAUSAL else 0 for _, label in train_rows])

        test_x = np.stack([vectors[question] for question, _ in test_rows])

        test_y = np.array([1 if label == CAUSAL else 0 for _, label in test_rows])

        (
            threshold,
            train_recall,
            train_precision,
        ) = calibrate_threshold(
            train_x,
            train_y,
        )

        clf = make_classifier()

        clf.fit(
            train_x,
            train_y,
        )

        scores = clf.decision_function(test_x)

        prediction = (scores >= threshold).astype(int)

        positives = int(np.sum(test_y))

        print()
        print(f"===== HOLD OUT {held_out.upper()} =====")
        print(f"threshold={threshold:.4f}")
        print(f"train_oof_recall={train_recall:.3f}")
        print(f"train_oof_precision={train_precision:.3f}")

        if positives == 0:
            print("heldout_recall=N/A")
            print("heldout_precision=N/A")
            print("dangerous_misroute_rate=N/A")
            continue

        recall = recall_score(
            test_y,
            prediction,
            zero_division=0,
        )

        precision = precision_score(
            test_y,
            prediction,
            zero_division=0,
        )

        dangerous = np.sum((test_y == 1) & (prediction == 0)) / positives

        print(f"heldout_recall={recall:.3f}")
        print(f"heldout_precision={precision:.3f}")
        print(f"dangerous_misroute_rate={dangerous:.3f}")


if __name__ == "__main__":
    main()
