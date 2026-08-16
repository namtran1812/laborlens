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
class BenchmarkCase:
    name: str
    question: str
    expected_intent: AskIntent
    expected_area: str | None
    expect_deterministic: bool


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    planner_correct: bool
    deterministic_correct: bool
    area_correct: bool
    guard_valid: bool
    latency_ms: float


CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        name="macro evidence",
        question="Which indicators contributed most?",
        expected_intent=AskIntent.MACRO_EVIDENCE,
        expected_area=None,
        expect_deterministic=True,
    ),
    BenchmarkCase(
        name="Florida weakness",
        question="Which Florida industries were weakening?",
        expected_intent=AskIntent.INDUSTRY_WEAKNESS,
        expected_area="12000",
        expect_deterministic=True,
    ),
    BenchmarkCase(
        name="Florida strength",
        question="Which Florida industries were outperforming?",
        expected_intent=AskIntent.INDUSTRY_STRENGTH,
        expected_area="12000",
        expect_deterministic=True,
    ),
    BenchmarkCase(
        name="point in time",
        question="Why does point-in-time data matter for Florida?",
        expected_intent=AskIntent.POINT_IN_TIME,
        expected_area="12000",
        expect_deterministic=True,
    ),
    BenchmarkCase(
        name="causal refusal",
        question=("Were hurricanes the reason Florida residential roofing employment weakened?"),
        expected_intent=AskIntent.CAUSAL_ATTRIBUTION,
        expected_area="12000",
        expect_deterministic=True,
    ),
    BenchmarkCase(
        name="interpretive synthesis",
        question=(
            "Give me a nuanced interpretation of this episode using the Florida industry context."
        ),
        expected_intent=AskIntent.GENERAL_RESEARCH,
        expected_area="12000",
        expect_deterministic=False,
    ),
)


def run_benchmark() -> list[BenchmarkResult]:
    store = ClickHouseStore(get_settings())

    pipeline = ResearchPipeline(store)

    results: list[BenchmarkResult] = []

    for case in CASES:
        started = perf_counter()

        plan = plan_question(case.question)

        bundle = pipeline.build(
            start_date=date(
                2024,
                6,
                1,
            ),
            as_of_date=date(
                2024,
                9,
                1,
            ),
            qcew_area_fips=(plan.area_fips if plan.needs_qcew else None),
            qcew_industry_level=6,
            qcew_context_limit=5,
        )

        guard_valid = True

        if plan.deterministic_answer:
            answer = deterministic_answer(
                plan=plan,
                bundle=bundle,
            )

            guard_valid = validate_ai_answer(answer.answer).valid

        elapsed_ms = (perf_counter() - started) * 1000.0

        results.append(
            BenchmarkResult(
                name=case.name,
                planner_correct=(plan.intent == case.expected_intent),
                deterministic_correct=(plan.deterministic_answer == case.expect_deterministic),
                area_correct=(plan.area_fips == case.expected_area),
                guard_valid=guard_valid,
                latency_ms=elapsed_ms,
            )
        )

    return results
