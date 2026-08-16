from laborlens.evaluation.assistant_reliability import (
    CAUSAL_QUESTIONS,
    planner_cases,
)


def test_planner_benchmark_has_meaningful_size():
    assert len(planner_cases()) >= 60


def test_causal_benchmark_has_multiple_adversarial_cases():
    assert len(CAUSAL_QUESTIONS) >= 10


def test_planner_benchmark_contains_all_core_intents():
    intents = {case.intent for case in planner_cases()}

    assert len(intents) >= 7
