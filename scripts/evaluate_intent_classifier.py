from __future__ import annotations

from collections import Counter

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import (
    StratifiedKFold,
)

from laborlens.api.intent_classifier import (
    training_examples,
)
from laborlens.api.semantic_router import model


def main() -> None:
    examples = training_examples()

    questions = [question for question, _ in examples]

    labels = np.array([intent.value for _, intent in examples])

    embeddings = model().encode(
        questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
    )

    counts = Counter(labels)

    print(
        "examples=",
        len(examples),
    )

    print("class_counts=")

    for label, count in sorted(counts.items()):
        print(f"  {label}={count}")

    splitter = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scores = []

    all_true = []
    all_pred = []

    for fold, (
        train_index,
        test_index,
    ) in enumerate(
        splitter.split(
            embeddings,
            labels,
        ),
        start=1,
    ):
        clf = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        )

        clf.fit(
            embeddings[train_index],
            labels[train_index],
        )

        predictions = clf.predict(embeddings[test_index])

        score = accuracy_score(
            labels[test_index],
            predictions,
        )

        scores.append(score)

        all_true.extend(labels[test_index])

        all_pred.extend(predictions)

        print(f"fold_{fold}_accuracy={score:.3f}")

    print()
    print(f"cv_mean_accuracy={np.mean(scores):.3f}")
    print(f"cv_std_accuracy={np.std(scores):.3f}")

    #
    # Safety recall across held-out folds.
    #
    causal_true = 0
    causal_correct = 0

    for true, predicted in zip(
        all_true,
        all_pred,
        strict=True,
    ):
        if true == "causal_attribution":
            causal_true += 1

            if predicted == "causal_attribution":
                causal_correct += 1

    print(f"cv_causal_recall={causal_correct / causal_true:.3f}")


if __name__ == "__main__":
    main()
