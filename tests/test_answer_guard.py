from laborlens.api.answer_guard import (
    validate_ai_answer,
)


def test_guard_rejects_negative_causal_assertion():
    result = validate_ai_answer("Hurricanes were not the reason employment weakened.")

    assert not result.valid


def test_guard_rejects_macro_contribution_as_decline():
    result = validate_ai_answer("PAYEMS, UNRATE, and ICSA all declined during the episode.")

    assert not result.valid


def test_guard_allows_standardized_contribution_language():
    result = validate_ai_answer(
        "PAYEMS had a negative standardized contribution to the regime score."
    )

    assert result.valid
