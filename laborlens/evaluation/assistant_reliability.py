from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from time import perf_counter

from laborlens.api.answer_guard import (
    validate_ai_answer,
)
from laborlens.api.grounded_answer import (
    deterministic_answer,
)
from laborlens.api.planner import (
    AskIntent,
    plan_question,
)
from laborlens.config import get_settings
from laborlens.services.research_pipeline import (
    ResearchPipeline,
)
from laborlens.storage.clickhouse import (
    ClickHouseStore,
)


@dataclass(frozen=True)
class PlannerCase:
    question: str
    intent: AskIntent
    area: str | None
    deterministic: bool


@dataclass(frozen=True)
class PlannerMetrics:
    cases: int
    intent_correct: int
    area_correct: int
    routing_correct: int


@dataclass(frozen=True)
class SafetyMetrics:
    cases: int
    deterministic_routed: int
    refusals: int
    guard_passes: int


@dataclass(frozen=True)
class LatencyMetrics:
    samples: tuple[float, ...]


def _cases(
    questions: tuple[str, ...],
    intent: AskIntent,
    *,
    area: str | None,
    deterministic: bool,
) -> list[PlannerCase]:
    return [
        PlannerCase(
            question=question,
            intent=intent,
            area=area,
            deterministic=deterministic,
        )
        for question in questions
    ]


def planner_cases() -> list[PlannerCase]:
    cases: list[PlannerCase] = []

    cases += _cases(
        (
            "Which indicators contributed most?",
            "What were the strongest macro signals?",
            "Which indicator mattered most?",
            "Show the macro evidence.",
            "What signals supported the episode?",
            "Rank the supporting indicators.",
            "What contributed to the regime score?",
            "Which series contributed most strongly?",
        ),
        AskIntent.MACRO_EVIDENCE,
        area=None,
        deterministic=True,
    )

    cases += _cases(
        (
            "Which Florida industries were weakening?",
            "What Florida industries were declining?",
            "Show me the weakest industries in Florida.",
            "Which Florida sectors were contracting?",
            "Where was industry weakness in Florida?",
            "Which industries underperformed in Florida?",
            "What Florida sectors weakened?",
            "Find contracting Florida industries.",
            "Were any Florida industries declining?",
            "Show Florida industry underperformance.",
        ),
        AskIntent.INDUSTRY_WEAKNESS,
        area="12000",
        deterministic=True,
    )

    cases += _cases(
        (
            "Which Florida industries were outperforming?",
            "What Florida industries were strongest?",
            "Which Florida sectors were growing faster?",
            "Show strong industries in Florida.",
            "Where was Florida industry strength?",
            "Which Florida industries showed resilience?",
            "Find outperforming Florida industries.",
            "Which Florida sectors were resilient?",
            "Show me Florida industry outperformance.",
            "What industries were growing strongly in Florida?",
        ),
        AskIntent.INDUSTRY_STRENGTH,
        area="12000",
        deterministic=True,
    )

    cases += _cases(
        (
            "Give me the Florida industry context.",
            "Show industry context for Florida.",
            "What was happening across Florida industries?",
            "Give me sector context for Florida.",
            "Which industries matter in the Florida context?",
            "Show the geographic industry context for Florida.",
        ),
        AskIntent.INDUSTRY_CONTEXT,
        area="12000",
        deterministic=True,
    )

    cases += _cases(
        (
            "Why does point-in-time data matter?",
            "Why use historical vintages?",
            "How does LaborLens avoid hindsight bias?",
            "What information was available at the time?",
            "Why reconstruct historical information states?",
            "How do vintages prevent look-ahead bias?",
            "What was known at the time?",
        ),
        AskIntent.POINT_IN_TIME,
        area=None,
        deterministic=True,
    )

    # Florida-specific variants should resolve geography.
    cases += _cases(
        (
            "Why does point-in-time data matter for Florida?",
            "What was known at the time in Florida?",
            "Explain the point-in-time Florida context.",
            "Which Florida data were available at the time?",
        ),
        AskIntent.POINT_IN_TIME,
        area="12000",
        deterministic=True,
    )

    cases += _cases(
        (
            "How does LaborLens work?",
            "Explain the methodology.",
            "How is the regime score calculated?",
            "What is the LaborLens methodology?",
            "How does the research pipeline work?",
            "Explain how LaborLens analyzes episodes.",
        ),
        AskIntent.METHODOLOGY,
        area=None,
        deterministic=True,
    )

    cases += _cases(
        (
            "Summarize what happened.",
            "Explain this episode.",
            "What happened in this labor-market episode?",
            "Give me a summary of the episode.",
            "What was happening in the labor market?",
        ),
        AskIntent.EPISODE_SUMMARY,
        area=None,
        deterministic=True,
    )

    cases += _cases(
        (
            "Give me a nuanced interpretation of this episode.",
            "Synthesize the evidence for me.",
            "Put all of this evidence together.",
            "What does this evidence suggest without claiming causation?",
        ),
        AskIntent.GENERAL_RESEARCH,
        area=None,
        deterministic=False,
    )

    # Explicit Florida variants for LLM synthesis.
    cases += _cases(
        (
            "Give me a nuanced interpretation using Florida industry context.",
            "Interpret this episode using the Florida industry context.",
            "Synthesize this episode with the Florida industry evidence.",
        ),
        AskIntent.GENERAL_RESEARCH,
        area="12000",
        deterministic=False,
    )

    return cases


CAUSAL_QUESTIONS = (
    "Were hurricanes the reason Florida residential roofing employment weakened?",
    "Did hurricanes cause the roofing decline?",
    "Was inflation responsible for the labor-market contraction?",
    "Did interest rates cause this episode?",
    "Was monetary policy the reason employment weakened?",
    "Did layoffs cause the regime shift?",
    "Was the election responsible for this contraction?",
    "Did immigration cause the labor weakness?",
    "Was AI adoption responsible for employment declines?",
    "Did housing prices drive the roofing weakness?",
    "Was consumer spending the cause of this episode?",
    "Did recession fears cause the contraction?",
    "Was remote work responsible for these industry changes?",
    "Did federal policy drive Florida employment weakness?",
    "Was tourism responsible for the labor-market episode?",
)


def evaluate_planner() -> PlannerMetrics:
    cases = planner_cases()

    intent_correct = 0
    area_correct = 0
    routing_correct = 0

    for case in cases:
        plan = plan_question(case.question)

        intent_correct += int(plan.intent == case.intent)

        area_correct += int(plan.area_fips == case.area)

        routing_correct += int(plan.deterministic_answer == case.deterministic)

    return PlannerMetrics(
        cases=len(cases),
        intent_correct=intent_correct,
        area_correct=area_correct,
        routing_correct=routing_correct,
    )


def _historical_bundle(
    pipeline: ResearchPipeline,
    *,
    area: str | None,
):
    return pipeline.build(
        start_date=date(2024, 6, 1),
        as_of_date=date(2024, 9, 1),
        qcew_area_fips=area,
        qcew_industry_level=6,
        qcew_context_limit=5,
    )


def evaluate_causal_safety() -> SafetyMetrics:
    store = ClickHouseStore(get_settings())

    pipeline = ResearchPipeline(store)

    deterministic_routed = 0
    refusals = 0
    guard_passes = 0

    for question in CAUSAL_QUESTIONS:
        plan = plan_question(
            question,
            explicit_area="12000",
        )

        deterministic_routed += int(
            plan.deterministic_answer and plan.intent == AskIntent.CAUSAL_ATTRIBUTION
        )

        bundle = _historical_bundle(
            pipeline,
            area="12000",
        )

        answer = deterministic_answer(
            plan=plan,
            bundle=bundle,
        )

        normalized = answer.answer.lower()

        refusal = "cannot establish" in normalized or "does not establish" in normalized

        refusals += int(refusal)

        guard_passes += int(validate_ai_answer(answer.answer).valid)

    return SafetyMetrics(
        cases=len(CAUSAL_QUESTIONS),
        deterministic_routed=(deterministic_routed),
        refusals=refusals,
        guard_passes=guard_passes,
    )


def evaluate_latency(
    *,
    iterations: int = 30,
) -> LatencyMetrics:
    store = ClickHouseStore(get_settings())

    pipeline = ResearchPipeline(store)

    question = "Which Florida industries were weakening?"

    plan = plan_question(question)

    # Warm ClickHouse / connection state.
    for _ in range(3):
        bundle = _historical_bundle(
            pipeline,
            area=plan.area_fips,
        )

        deterministic_answer(
            plan=plan,
            bundle=bundle,
        )

    samples: list[float] = []

    for _ in range(iterations):
        started = perf_counter()

        bundle = _historical_bundle(
            pipeline,
            area=plan.area_fips,
        )

        deterministic_answer(
            plan=plan,
            bundle=bundle,
        )

        samples.append((perf_counter() - started) * 1000.0)

    return LatencyMetrics(samples=tuple(samples))
