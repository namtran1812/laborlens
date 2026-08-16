from laborlens.api.planner import (
    AskIntent,
    plan_question,
)


def test_plans_florida_industry_weakness():
    plan = plan_question("Which Florida industries were weakening?")

    assert plan.intent == AskIntent.INDUSTRY_WEAKNESS
    assert plan.area_fips == "12000"
    assert plan.needs_qcew
    assert plan.deterministic_answer


def test_macro_evidence_does_not_require_qcew():
    plan = plan_question("Which indicators contributed most?")

    assert plan.intent == AskIntent.MACRO_EVIDENCE
    assert not plan.needs_qcew


def test_explicit_area_overrides_parser():
    plan = plan_question(
        "Which industries were weakening?",
        explicit_area="12000",
    )

    assert plan.area_fips == "12000"
    assert plan.needs_qcew


def test_general_question_can_fall_back_to_llm():
    plan = plan_question("Give me a nuanced interpretation of this episode.")

    assert plan.intent == AskIntent.GENERAL_RESEARCH
    assert not plan.deterministic_answer


def test_plans_industry_weakness_with_geography_in_phrase():
    plan = plan_question("What Florida industries are declining?")

    assert plan.intent == AskIntent.INDUSTRY_WEAKNESS
    assert plan.area_fips == "12000"


def test_plans_florida_industry_strength():
    plan = plan_question("Which Florida industries are outperforming?")

    assert plan.intent == AskIntent.INDUSTRY_STRENGTH
    assert plan.area_fips == "12000"


def test_weakness_and_strength_are_distinct_intents():
    weak = plan_question("Which Florida industries were weakening?")

    strong = plan_question("Which Florida industries were outperforming?")

    assert weak.intent == AskIntent.INDUSTRY_WEAKNESS
    assert strong.intent == AskIntent.INDUSTRY_STRENGTH


def test_nuanced_interpretation_uses_llm_with_qcew():
    plan = plan_question(
        "Give me a nuanced interpretation of this episode using the Florida industry context."
    )

    assert plan.intent == AskIntent.GENERAL_RESEARCH
    assert plan.area_fips == "12000"
    assert plan.needs_qcew
    assert not plan.deterministic_answer


def test_direct_industry_context_stays_deterministic():
    plan = plan_question("Give me the Florida industry context.")

    assert plan.intent == AskIntent.INDUSTRY_CONTEXT
    assert plan.area_fips == "12000"
    assert plan.deterministic_answer


def test_causal_question_is_deterministic():
    plan = plan_question(
        "Were hurricanes the reason Florida residential roofing employment weakened?"
    )

    assert plan.intent == AskIntent.CAUSAL_ATTRIBUTION
    assert plan.area_fips == "12000"
    assert plan.deterministic_answer


def test_semantic_macro_evidence_paraphrase():
    plan = plan_question("Which data series had the biggest effect?")

    assert plan.intent == AskIntent.MACRO_EVIDENCE


def test_semantic_relative_weakness_paraphrase():
    plan = plan_question("Where did Florida employment lag the nation?")

    assert plan.intent == AskIntent.INDUSTRY_WEAKNESS
    assert plan.area_fips == "12000"


def test_semantic_relative_strength_paraphrase():
    plan = plan_question("Where did Florida beat national employment growth?")

    assert plan.intent == AskIntent.INDUSTRY_STRENGTH
    assert plan.area_fips == "12000"


def test_semantic_point_in_time_paraphrase():
    plan = plan_question("How do you prevent future information from entering this analysis?")

    assert plan.intent == AskIntent.POINT_IN_TIME


def test_semantic_methodology_paraphrase():
    plan = plan_question("How are individual signals combined?")

    assert plan.intent == AskIntent.METHODOLOGY


def test_semantic_causal_produce_paraphrase():
    plan = plan_question("Did higher borrowing costs produce this labor weakness?")

    assert plan.intent == AskIntent.CAUSAL_ATTRIBUTION
    assert plan.deterministic_answer


def test_reasonable_does_not_match_reason():
    plan = plan_question("What is a reasonable interpretation of the overall evidence?")

    assert plan.intent == AskIntent.GENERAL_RESEARCH
    assert not plan.deterministic_answer


def test_causal_intent_beats_industry_weakness_polarity():
    plan = plan_question("Was monetary policy the reason Florida employment weakened?")

    assert plan.intent == AskIntent.CAUSAL_ATTRIBUTION
    assert plan.area_fips == "12000"
    assert plan.deterministic_answer


def test_point_in_time_with_area_requests_qcew():
    plan = plan_question(
        (
            "Explain why the Florida QCEW quarter "
            "is legitimate for this historical "
            "information state."
        ),
        explicit_area="12000",
    )

    assert plan.intent == AskIntent.POINT_IN_TIME
    assert plan.area_fips == "12000"
    assert plan.needs_qcew
    assert plan.needs_macro
    assert plan.deterministic_answer


def test_point_in_time_without_area_does_not_require_qcew():
    plan = plan_question(
        "Why does the historical information state matter when interpreting this episode?"
    )

    assert plan.intent == AskIntent.POINT_IN_TIME
    assert plan.area_fips is None
    assert not plan.needs_qcew
    assert plan.needs_macro
    assert plan.deterministic_answer


def test_point_in_time_with_area_still_requires_qcew():
    plan = plan_question(
        (
            "Explain why the Florida QCEW quarter "
            "is legitimate for this historical "
            "information state."
        ),
        explicit_area="12000",
    )

    assert plan.intent == AskIntent.POINT_IN_TIME
    assert plan.area_fips == "12000"
    assert plan.needs_qcew
    assert plan.needs_macro
    assert plan.deterministic_answer
