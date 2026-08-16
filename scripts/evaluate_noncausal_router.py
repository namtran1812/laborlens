from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
)
from sklearn.svm import LinearSVC

from benchmarks.holdout_v3 import CASES as V3_CASES
from laborlens.api.semantic_router import model
from laborlens.evaluation.assistant_holdout import holdout_cases
from laborlens.evaluation.assistant_holdout_v2 import CASES as V2_CASES
from laborlens.evaluation.assistant_reliability import planner_cases

CAUSAL = "causal_attribution"


def corpora():
    return {
        "dev": [(case.question, case.intent.value) for case in planner_cases()],
        "v1": [(case.question, case.intent.value) for case in holdout_cases()],
        "v2": [(case.question, case.intent.value) for case in V2_CASES],
        "v3": [(case.question, case.intent.value) for case in V3_CASES],
    }


def deduplicate(rows):
    return list(dict(rows).items())


def main():
    data = corpora()

    questions = list(
        dict.fromkeys(
            question for rows in data.values() for question, label in rows if label != CAUSAL
        )
    )

    embeddings = model().encode(
        questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    vectors = {question: embeddings[index] for index, question in enumerate(questions)}

    scores = []

    for held_out in data:
        train_rows = deduplicate(
            [
                row
                for name, rows in data.items()
                if name != held_out
                for row in rows
                if row[1] != CAUSAL
            ]
        )

        test_rows = deduplicate([row for row in data[held_out] if row[1] != CAUSAL])

        train_x = np.stack([vectors[question] for question, _ in train_rows])

        train_y = np.array([label for _, label in train_rows])

        test_x = np.stack([vectors[question] for question, _ in test_rows])

        test_y = np.array([label for _, label in test_rows])

        clf = LinearSVC(
            C=1.0,
            class_weight="balanced",
            random_state=42,
        )

        clf.fit(
            train_x,
            train_y,
        )

        prediction = clf.predict(test_x)

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

        scores.append(
            (
                accuracy,
                macro_f1,
            )
        )

        print()
        print(f"===== HOLD OUT {held_out.upper()} =====")
        print(f"accuracy={accuracy:.3f}")
        print(f"macro_f1={macro_f1:.3f}")

    print()
    print("===== MEAN =====")
    print(f"accuracy={np.mean([x[0] for x in scores]):.3f}")
    print(f"macro_f1={np.mean([x[1] for x in scores]):.3f}")


if __name__ == "__main__":
    main()
