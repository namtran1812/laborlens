from __future__ import annotations

from dataclasses import dataclass

from laborlens.api.planner import (
    AskIntent,
    plan_question,
)


@dataclass(frozen=True)
class HoldoutCase:
    question: str
    intent: AskIntent
    area: str | None
    deterministic: bool


def _make(
    questions: tuple[str, ...],
    intent: AskIntent,
    *,
    area: str | None = None,
    deterministic: bool = True,
) -> list[HoldoutCase]:
    return [
        HoldoutCase(
            question=q,
            intent=intent,
            area=area,
            deterministic=deterministic,
        )
        for q in questions
    ]


def holdout_cases() -> list[HoldoutCase]:
    cases: list[HoldoutCase] = []

    # 15 macro-evidence questions
    cases += _make(
        (
            "What evidence was most important?",
            "Which labor indicators had the largest contributions?",
            "Show me the dominant economic signals.",
            "What evidence most strongly supported the classification?",
            "Which data series had the biggest effect?",
            "Break down the macro signals behind this episode.",
            "What are the main supporting labor indicators?",
            "Which economic series mattered most here?",
            "What signals dominate the evidence?",
            "Give me the indicator contribution breakdown.",
            "What evidence supports the broad contraction label?",
            "Which macro series had the largest standardized contributions?",
            "Show the strongest evidence behind the regime.",
            "What labor signals were most influential?",
            "Rank the macro evidence by contribution.",
        ),
        AskIntent.MACRO_EVIDENCE,
    )

    # 12 Florida weakness questions
    cases += _make(
        (
            "Where did Florida employment lag the nation?",
            "Which Florida industries performed worse than their national peers?",
            "Show sectors with relative deterioration in Florida.",
            "Where was Florida losing ground relative to the US?",
            "Which Florida industries showed negative relative gaps?",
            "Find areas of sectoral weakness in Florida.",
            "What Florida industries lagged nationally?",
            "Which Florida sectors had worse year-over-year performance?",
            "Where does Florida show employment underperformance?",
            "Identify Florida industries with local contraction.",
            "Which Florida industries deteriorated relative to national trends?",
            "Show me weak Florida employment sectors.",
        ),
        AskIntent.INDUSTRY_WEAKNESS,
        area="12000",
    )

    # 12 Florida strength questions
    cases += _make(
        (
            "Where did Florida beat national employment growth?",
            "Which Florida industries performed better than the US?",
            "Show sectors with positive relative performance in Florida.",
            "Where was Florida gaining ground against national trends?",
            "Which Florida industries had positive relative gaps?",
            "Find areas of sectoral strength in Florida.",
            "What Florida industries beat their national counterparts?",
            "Which Florida sectors had better year-over-year performance?",
            "Where does Florida show employment outperformance?",
            "Identify Florida industries with relative strength.",
            "Which Florida industries held up better than national peers?",
            "Show me resilient Florida employment sectors.",
        ),
        AskIntent.INDUSTRY_STRENGTH,
        area="12000",
    )

    # 10 generic industry-context questions
    cases += _make(
        (
            "Give me a sector-level view of Florida.",
            "What does the Florida industry breakdown look like?",
            "Show the cross-sectional Florida employment picture.",
            "What do Florida industry comparisons show?",
            "Give me the Florida sector breakdown for this analysis.",
            "What is the industry-level picture in Florida?",
            "Show relevant Florida sector evidence.",
            "How do Florida industries compare with national peers?",
            "Give me cross-sectional context for Florida employment.",
            "What does QCEW show across Florida sectors?",
        ),
        AskIntent.INDUSTRY_CONTEXT,
        area="12000",
    )

    # 12 point-in-time questions
    cases += _make(
        (
            "How do you prevent future information from entering this analysis?",
            "Does this analysis use data that was actually available then?",
            "How do you avoid using revised data from the future?",
            "Explain the historical data cutoff.",
            "How is lookahead leakage prevented?",
            "How do you recreate what an analyst could have known then?",
            "Does the analysis respect publication dates?",
            "How are historical data releases handled?",
            "Explain the vintage-data logic.",
            "How do you enforce the as-of date?",
            "Why are release dates important here?",
            "How do you keep future observations out of a historical analysis?",
        ),
        AskIntent.POINT_IN_TIME,
    )

    # 10 methodology questions
    cases += _make(
        (
            "Walk me through the analytical procedure.",
            "How are labor-market episodes detected?",
            "Explain the scoring procedure.",
            "How are individual signals combined?",
            "What steps produce an episode classification?",
            "Describe the research engine.",
            "How does the system transform indicators into claims?",
            "Explain the analytical workflow from data to episode.",
            "How are adjacent signals converted into episodes?",
            "What procedure does LaborLens use to validate claims?",
        ),
        AskIntent.METHODOLOGY,
    )

    # 9 episode-summary questions
    cases += _make(
        (
            "Give me the short version of this episode.",
            "Describe the labor-market episode.",
            "What is the main takeaway from this episode?",
            "Give me an overview of what occurred.",
            "Recap this labor-market period.",
            "What does the episode say at a high level?",
            "Give me the episode overview.",
            "Briefly describe what the system detected.",
            "What did LaborLens detect in this period?",
        ),
        AskIntent.EPISODE_SUMMARY,
    )

    # 10 causal questions — all MUST remain deterministic.
    cases += _make(
        (
            "Did higher borrowing costs produce this labor weakness?",
            "Can we blame the employment deterioration on inflation?",
            "Was a slowdown in construction responsible for this episode?",
            "Can the contraction be attributed to monetary tightening?",
            "Did automation produce these employment patterns?",
            "Was weak consumer demand responsible for the contraction?",
            "Can we say housing conditions produced the roofing decline?",
            "Did government spending create the observed labor pattern?",
            "Was economic uncertainty responsible for these changes?",
        ),
        AskIntent.CAUSAL_ATTRIBUTION,
        area=None,
    )

    # Geography-bearing causal holdout.
    cases += _make(
        ("Did weather events produce the Florida employment changes?",),
        AskIntent.CAUSAL_ATTRIBUTION,
        area="12000",
    )

    # 10 genuine synthesis questions — should reach AI.
    cases += _make(
        (
            "Develop a careful interpretation of the evidence.",
            "What broader interpretation can we draw from these results?",
            "Synthesize the macro and cross-sectional evidence.",
            "Give me a careful reading of what these results imply.",
            "How should an analyst interpret the evidence as a whole?",
            "Provide a balanced interpretation of this labor episode.",
            "Connect the different pieces of evidence without overstating them.",
            "Give me an analytical interpretation of these findings.",
            "What is a reasonable interpretation of the overall evidence?",
            "Put the findings into a coherent analytical narrative.",
        ),
        AskIntent.GENERAL_RESEARCH,
        deterministic=False,
    )

    return cases


@dataclass(frozen=True)
class HoldoutResult:
    total: int
    intent_correct: int
    area_correct: int
    routing_correct: int
    causal_total: int
    causal_correct: int


def evaluate_holdout() -> tuple[
    HoldoutResult,
    list[tuple[HoldoutCase, object]],
]:
    cases = holdout_cases()

    intent_correct = 0
    area_correct = 0
    routing_correct = 0
    causal_total = 0
    causal_correct = 0

    failures: list[tuple[HoldoutCase, object]] = []

    for case in cases:
        plan = plan_question(case.question)

        intent_ok = plan.intent == case.intent
        area_ok = plan.area_fips == case.area
        routing_ok = plan.deterministic_answer == case.deterministic

        intent_correct += int(intent_ok)
        area_correct += int(area_ok)
        routing_correct += int(routing_ok)

        if case.intent == AskIntent.CAUSAL_ATTRIBUTION:
            causal_total += 1
            causal_correct += int(intent_ok and plan.deterministic_answer)

        if not (intent_ok and area_ok and routing_ok):
            failures.append(
                (
                    case,
                    plan,
                )
            )

    return (
        HoldoutResult(
            total=len(cases),
            intent_correct=intent_correct,
            area_correct=area_correct,
            routing_correct=routing_correct,
            causal_total=causal_total,
            causal_correct=causal_correct,
        ),
        failures,
    )
