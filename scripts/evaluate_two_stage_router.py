from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
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

CAUSAL = "causal_attribution"


def corpora() -> dict[str, list[tuple[str, str]]]:
    return {
        "dev": [(case.question, case.intent.value) for case in planner_cases()],
        "v1": [(case.question, case.intent.value) for case in holdout_cases()],
        "v2": [(case.question, case.intent.value) for case in V2_CASES],
        "v3": [(case.question, case.intent.value) for case in V3_CASES],
    }


def deduplicate(
    rows: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    return list(dict(rows).items())


def make_causal_classifier() -> LinearSVC:
    return LinearSVC(
        class_weight={
            0: 1.0,
            1: 3.0,
        },
        C=1.0,
        random_state=42,
    )


def calibrate_threshold(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float, float]:
    """
    Choose the highest threshold that achieves perfect
    out-of-fold causal recall on the training data.

    Higher threshold -> fewer false positives.
    We therefore maximize precision subject to recall == 1.
    """
    causal_count = int(np.sum(y == 1))

    noncausal_count = int(np.sum(y == 0))

    if causal_count < 2:
        raise RuntimeError("Not enough causal examples for calibration")

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

    #
    # Candidate thresholds from observed OOF scores,
    # plus a value slightly below the minimum.
    #
    candidates = np.unique(
        np.concatenate(
            (
                oof_scores,
                np.array([float(np.min(oof_scores) - 1e-6)]),
            )
        )
    )

    best_threshold = float(np.min(candidates))
    best_precision = 0.0
    best_recall = 0.0

    for threshold in sorted(
        candidates,
        reverse=True,
    ):
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

        best_threshold = float(threshold)
        best_precision = float(precision)
        best_recall = float(recall)

        #
        # Thresholds are descending, so the first one
        # satisfying full recall is the most selective.
        #
        break

    return (
        best_threshold,
        best_recall,
        best_precision,
    )


def main() -> None:
    data = corpora()

    questions = list(dict.fromkeys(question for rows in data.values() for question, _ in rows))

    embeddings = model().encode(
        questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    vectors = {question: embeddings[index] for index, question in enumerate(questions)}

    for held_out in data:
        train_rows = deduplicate(
            [row for name, rows in data.items() if name != held_out for row in rows]
        )

        test_rows = deduplicate(data[held_out])

        train_x = np.stack([vectors[question] for question, _ in train_rows])

        test_x = np.stack([vectors[question] for question, _ in test_rows])

        train_labels = np.array([label for _, label in train_rows])

        test_labels = np.array([label for _, label in test_rows])

        train_causal = (train_labels == CAUSAL).astype(int)

        test_causal = (test_labels == CAUSAL).astype(int)

        #
        # Calibrate using TRAINING DATA ONLY.
        #
        (
            threshold,
            calibration_recall,
            calibration_precision,
        ) = calibrate_threshold(
            train_x,
            train_causal,
        )

        causal_clf = make_causal_classifier()

        causal_clf.fit(
            train_x,
            train_causal,
        )

        test_scores = causal_clf.decision_function(test_x)

        causal_prediction = (test_scores >= threshold).astype(int)

        causal_total = int(np.sum(test_causal))

        if causal_total:
            heldout_recall = recall_score(
                test_causal,
                causal_prediction,
                zero_division=0,
            )

            heldout_precision = precision_score(
                test_causal,
                causal_prediction,
                zero_division=0,
            )

            causal_missed = int(np.sum((test_causal == 1) & (causal_prediction == 0)))

            dangerous_rate = causal_missed / causal_total
        else:
            heldout_recall = None
            heldout_precision = None
            dangerous_rate = None

        #
        # Stage 2: non-causal multiclass router.
        #
        noncausal_train = train_labels != CAUSAL

        intent_clf = LinearSVC(
            class_weight="balanced",
            C=1.0,
            random_state=42,
        )

        intent_clf.fit(
            train_x[noncausal_train],
            train_labels[noncausal_train],
        )

        stage2_prediction = intent_clf.predict(test_x)

        final_prediction = stage2_prediction.copy()

        final_prediction[causal_prediction == 1] = CAUSAL

        accuracy = accuracy_score(
            test_labels,
            final_prediction,
        )

        macro_f1 = f1_score(
            test_labels,
            final_prediction,
            average="macro",
            zero_division=0,
        )

        print()
        print(f"===== HOLD OUT {held_out.upper()} =====")

        print(f"calibrated_threshold={threshold:.4f}")
        print(f"train_oof_causal_recall={calibration_recall:.3f}")
        print(f"train_oof_causal_precision={calibration_precision:.3f}")

        print(f"accuracy={accuracy:.3f}")
        print(f"macro_f1={macro_f1:.3f}")

        if heldout_recall is None:
            print("causal_recall=N/A")
            print("causal_precision=N/A")
            print("dangerous_misroute_rate=N/A")
        else:
            print(f"causal_recall={heldout_recall:.3f}")
            print(f"causal_precision={heldout_precision:.3f}")
            print(f"dangerous_misroute_rate={dangerous_rate:.3f}")


if __name__ == "__main__":
    main()
