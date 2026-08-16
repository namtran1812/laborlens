from laborlens.api.planner import (
    AskIntent,
)
from laborlens.evaluation.assistant_holdout_v2 import (
    CASES,
)


def test_holdout_v2_is_large_enough():
    assert len(CASES) >= 50


def test_holdout_v2_questions_are_unique():
    questions = [case.question for case in CASES]

    assert len(questions) == len(set(questions))


def test_holdout_v2_contains_causal_cases():
    assert sum(case.intent == AskIntent.CAUSAL_ATTRIBUTION for case in CASES) >= 10


def test_holdout_v2_contains_llm_cases():
    assert sum(not case.deterministic for case in CASES) >= 5
