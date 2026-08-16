from __future__ import annotations

from math import ceil

from laborlens.evaluation.assistant_reliability import (
    evaluate_causal_safety,
    evaluate_latency,
    evaluate_planner,
)


def percentile(
    values: tuple[float, ...],
    p: float,
) -> float:
    ordered = sorted(values)

    index = max(
        0,
        min(
            len(ordered) - 1,
            ceil(p * len(ordered)) - 1,
        ),
    )

    return ordered[index]


def rate(
    numerator: int,
    denominator: int,
) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def main() -> None:
    planner = evaluate_planner()
    safety = evaluate_causal_safety()
    latency = evaluate_latency()

    print("===== PLANNER =====")
    print(f"planner_cases={planner.cases}")
    print(f"intent_accuracy={rate(planner.intent_correct, planner.cases):.3f}")
    print(f"area_accuracy={rate(planner.area_correct, planner.cases):.3f}")
    print(f"routing_accuracy={rate(planner.routing_correct, planner.cases):.3f}")

    print()
    print("===== CAUSAL SAFETY =====")
    print(f"causal_cases={safety.cases}")
    print(f"causal_routing_rate={rate(safety.deterministic_routed, safety.cases):.3f}")
    print(f"causal_refusal_rate={rate(safety.refusals, safety.cases):.3f}")
    print(f"causal_guard_pass_rate={rate(safety.guard_passes, safety.cases):.3f}")

    print()
    print("===== PLANNER FAILURES =====")

    from laborlens.api.planner import (
        plan_question,
    )
    from laborlens.evaluation.assistant_reliability import (
        planner_cases,
    )

    failures = 0

    for case in planner_cases():
        plan = plan_question(case.question)

        if (
            plan.intent != case.intent
            or plan.area_fips != case.area
            or (plan.deterministic_answer != case.deterministic)
        ):
            failures += 1

            print(f"question={case.question!r}")
            print(f"  expected_intent={case.intent}")
            print(f"  actual_intent={plan.intent}")
            print(f"  expected_area={case.area}")
            print(f"  actual_area={plan.area_fips}")
            print(f"  expected_deterministic={case.deterministic}")
            print(f"  actual_deterministic={plan.deterministic_answer}")
            print()

    print(f"planner_failures={failures}")

    print()
    print("===== CAUSAL FAILURES =====")

    from laborlens.api.planner import (
        AskIntent,
        plan_question,
    )
    from laborlens.evaluation.assistant_reliability import (
        CAUSAL_QUESTIONS,
    )

    causal_failures = 0

    for question in CAUSAL_QUESTIONS:
        plan = plan_question(
            question,
            explicit_area="12000",
        )

        if plan.intent != AskIntent.CAUSAL_ATTRIBUTION or not plan.deterministic_answer:
            causal_failures += 1

            print(f"question={question!r}")
            print(f"  actual_intent={plan.intent}")
            print(f"  deterministic={plan.deterministic_answer}")
            print()

    print(f"causal_failures={causal_failures}")

    samples = latency.samples

    print()
    print("===== LATENCY =====")
    print(f"latency_samples={len(samples)}")
    print(f"latency_p50_ms={percentile(samples, 0.50):.2f}")
    print(f"latency_p95_ms={percentile(samples, 0.95):.2f}")
    print(f"latency_p99_ms={percentile(samples, 0.99):.2f}")
    print(f"latency_min_ms={min(samples):.2f}")
    print(f"latency_max_ms={max(samples):.2f}")


if __name__ == "__main__":
    main()
