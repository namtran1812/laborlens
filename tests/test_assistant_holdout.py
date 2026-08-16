from laborlens.evaluation.assistant_holdout import (
    holdout_cases,
)


def test_holdout_has_100_cases():
    assert len(holdout_cases()) == 100


def test_holdout_questions_are_unique():
    questions = [case.question for case in holdout_cases()]

    assert len(questions) == len(set(questions))
