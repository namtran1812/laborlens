from __future__ import annotations

from collections import defaultdict

import numpy as np
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    recall_score,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC

from benchmarks.holdout_v3 import CASES as V3_CASES
from laborlens.api.semantic_router import model
from laborlens.evaluation.assistant_holdout import (
    holdout_cases,
)
from laborlens.evaluation.assistant_holdout_v2 import (
    CASES as V2_CASES,
)
from laborlens.evaluation.assistant_reliability import (
    planner_cases,
)

CAUSAL = "causal_attribution"
GENERAL = "general_research"


def corpora() -> dict[
    str,
    list[tuple[str, str]],
]:
    return {
        "dev": [
            (
                case.question,
                case.intent.value,
            )
            for case in planner_cases()
        ],
        "v1": [
            (
                case.question,
                case.intent.value,
            )
            for case in holdout_cases()
        ],
        "v2": [
            (
                case.question,
                case.intent.value,
            )
            for case in V2_CASES
        ],
        "v3": [
            (
                case.question,
                case.intent.value,
            )
            for case in V3_CASES
        ],
    }


def deduplicate(
    rows: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}

    for question, label in rows:
        seen[question] = label

    return list(seen.items())


def causal_recall(
    truth: np.ndarray,
    predicted: np.ndarray,
) -> float:
    truth_binary = truth == CAUSAL

    prediction_binary = predicted == CAUSAL

    return recall_score(
        truth_binary,
        prediction_binary,
        zero_division=0,
    )


def general_recall(
    truth: np.ndarray,
    predicted: np.ndarray,
) -> float:
    truth_binary = truth == GENERAL

    prediction_binary = predicted == GENERAL

    return recall_score(
        truth_binary,
        prediction_binary,
        zero_division=0,
    )


def main() -> None:
    data = corpora()

    all_questions = []

    for rows in data.values():
        all_questions.extend(question for question, _ in rows)

    #
    # Encode every unique question once.
    #
    unique_questions = list(dict.fromkeys(all_questions))

    print(
        "unique_questions=",
        len(unique_questions),
    )

    embeddings = model().encode(
        unique_questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    embedding_by_question = {
        question: embeddings[index] for index, question in enumerate(unique_questions)
    }

    models = {
        "logistic": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            C=1.0,
            random_state=42,
        ),
        "linear_svm": LinearSVC(
            C=1.0,
            class_weight="balanced",
            random_state=42,
        ),
        "cosine_knn_5": KNeighborsClassifier(
            n_neighbors=5,
            metric="cosine",
            weights="distance",
        ),
        "cosine_knn_9": KNeighborsClassifier(
            n_neighbors=9,
            metric="cosine",
            weights="distance",
        ),
    }

    aggregate: dict[
        str,
        dict[str, list[float]],
    ] = defaultdict(lambda: defaultdict(list))

    for held_out_name in data:
        training_rows: list[tuple[str, str]] = []

        for name, rows in data.items():
            if name != held_out_name:
                training_rows.extend(rows)

        training_rows = deduplicate(training_rows)

        test_rows = deduplicate(data[held_out_name])

        train_x = np.stack([embedding_by_question[question] for question, _ in training_rows])

        train_y = np.array([label for _, label in training_rows])

        test_x = np.stack([embedding_by_question[question] for question, _ in test_rows])

        test_y = np.array([label for _, label in test_rows])

        print()
        print(f"===== HOLD OUT {held_out_name.upper()} =====")
        print(f"train={len(training_rows)}")
        print(f"test={len(test_rows)}")

        for model_name, prototype in models.items():
            classifier = clone(prototype)

            classifier.fit(
                train_x,
                train_y,
            )

            prediction = classifier.predict(test_x)

            accuracy = accuracy_score(
                test_y,
                prediction,
            )

            macro_f1 = f1_score(
                test_y,
                prediction,
                average="macro",
                zero_division=0,
            )

            causal = causal_recall(
                test_y,
                prediction,
            )

            general = general_recall(
                test_y,
                prediction,
            )

            aggregate[model_name]["accuracy"].append(accuracy)

            aggregate[model_name]["macro_f1"].append(macro_f1)

            aggregate[model_name]["causal_recall"].append(causal)

            aggregate[model_name]["general_recall"].append(general)

            print(
                f"{model_name}: "
                f"accuracy={accuracy:.3f} "
                f"macro_f1={macro_f1:.3f} "
                f"causal_recall={causal:.3f} "
                f"general_recall={general:.3f}"
            )

    print()
    print("===== CROSS-CORPUS MEANS =====")

    for model_name in models:
        metrics = aggregate[model_name]

        print(
            f"{model_name}: "
            f"accuracy="
            f"{np.mean(metrics['accuracy']):.3f} "
            f"macro_f1="
            f"{np.mean(metrics['macro_f1']):.3f} "
            f"causal_recall="
            f"{np.mean(metrics['causal_recall']):.3f} "
            f"general_recall="
            f"{np.mean(metrics['general_recall']):.3f}"
        )


if __name__ == "__main__":
    main()
