from __future__ import annotations

from collections import Counter
from time import perf_counter

from benchmarks.holdout_v3 import CASES
from laborlens.api.planner import AskIntent, plan_question


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    index = round((len(values) - 1) * q)
    return values[index]


def main() -> None:
    failures = []
    confusion: Counter[tuple[str, str]] = Counter()

    intent_correct = 0
    area_correct = 0
    routing_correct = 0

    safety_total = 0
    safety_correct = 0
    dangerous_misroutes = 0

    ambiguous_total = 0
    ambiguous_correct = 0

    latencies = []

    # Warm model before measuring.
    plan_question("Which indicators contributed most?")

    for case in CASES:
        start = perf_counter()

        plan = plan_question(
            case.question,
        )

        latencies.append((perf_counter() - start) * 1000)

        intent_ok = plan.intent == case.intent
        area_ok = plan.area_fips == case.area_fips
        route_ok = plan.deterministic_answer == case.deterministic

        intent_correct += intent_ok
        area_correct += area_ok
        routing_correct += route_ok

        if not intent_ok:
            confusion[
                (
                    case.intent.value,
                    plan.intent.value,
                )
            ] += 1

        if case.safety_critical:
            safety_total += 1

            if plan.intent == AskIntent.CAUSAL_ATTRIBUTION and plan.deterministic_answer:
                safety_correct += 1

            if not plan.deterministic_answer:
                dangerous_misroutes += 1

        if case.intent == AskIntent.GENERAL_RESEARCH:
            ambiguous_total += 1

            if plan.intent == AskIntent.GENERAL_RESEARCH and not plan.deterministic_answer:
                ambiguous_correct += 1

        if not (intent_ok and area_ok and route_ok):
            failures.append(
                (
                    case,
                    plan,
                    intent_ok,
                    area_ok,
                    route_ok,
                )
            )

    n = len(CASES)

    print("===== HOLDOUT V3 =====")
    print(f"cases={n}")
    print(f"intent_accuracy={intent_correct / n:.3f}")
    print(f"area_accuracy={area_correct / n:.3f}")
    print(f"routing_accuracy={routing_correct / n:.3f}")

    print()
    print("===== SAFETY =====")
    print(f"safety_cases={safety_total}")
    print(f"causal_safety_recall={safety_correct / safety_total:.3f}")
    print(f"dangerous_misroute_rate={dangerous_misroutes / safety_total:.3f}")

    print()
    print("===== SAFE ABSTENTION =====")
    print(f"general_cases={ambiguous_total}")
    print(f"general_research_accuracy={ambiguous_correct / ambiguous_total:.3f}")

    print()
    print("===== ROUTER LATENCY =====")
    print(f"samples={len(latencies)}")
    print(f"p50_ms={percentile(latencies, 0.50):.2f}")
    print(f"p95_ms={percentile(latencies, 0.95):.2f}")
    print(f"p99_ms={percentile(latencies, 0.99):.2f}")

    print()
    print("===== CONFUSION =====")

    if not confusion:
        print("none")
    else:
        for (
            expected,
            actual,
        ), count in confusion.most_common():
            print(f"{expected} -> {actual}: {count}")

    print()
    print("===== FAILURES =====")

    for (
        case,
        plan,
        intent_ok,
        area_ok,
        route_ok,
    ) in failures:
        print(f"question={case.question!r}")
        print(f"  expected_intent={case.intent.value}")
        print(f"  actual_intent={plan.intent.value}")
        print(f"  expected_area={case.area_fips}")
        print(f"  actual_area={plan.area_fips}")
        print(f"  expected_deterministic={case.deterministic}")
        print(f"  actual_deterministic={plan.deterministic_answer}")
        print(f"  intent_ok={intent_ok} area_ok={area_ok} route_ok={route_ok}")
        print()

    print(f"failures={len(failures)}")


if __name__ == "__main__":
    main()
