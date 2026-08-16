from __future__ import annotations

from collections import Counter
from statistics import median
from time import perf_counter

from benchmarks.holdout_v4 import CASES
from laborlens.api.planner import AskIntent, plan_question


def percentile(
    values: list[float],
    q: float,
) -> float:
    ordered = sorted(values)

    index = round((len(ordered) - 1) * q)

    return ordered[index]


def main() -> None:
    #
    # Warm the production router before timing.
    #
    plan_question("Which indicators contributed most?")

    intent_correct = 0
    area_correct = 0
    routing_correct = 0

    safety_total = 0
    safety_correct = 0
    dangerous_misroutes = 0

    general_total = 0
    general_correct = 0

    failures = []
    confusion = Counter()
    latencies = []

    for case in CASES:
        started = perf_counter()

        plan = plan_question(case.question)

        latencies.append((perf_counter() - started) * 1000.0)

        intent_ok = plan.intent == case.intent

        area_ok = plan.area_fips == case.area_fips

        route_ok = plan.deterministic_answer == case.deterministic

        intent_correct += int(intent_ok)

        area_correct += int(area_ok)

        routing_correct += int(route_ok)

        if not intent_ok:
            confusion[
                (
                    case.intent.value,
                    plan.intent.value,
                )
            ] += 1

        if case.safety_critical:
            safety_total += 1

            safe = plan.intent == AskIntent.CAUSAL_ATTRIBUTION and plan.deterministic_answer

            safety_correct += int(safe)

            if not plan.deterministic_answer:
                dangerous_misroutes += 1

        if case.intent == AskIntent.GENERAL_RESEARCH:
            general_total += 1

            correct_general = (
                plan.intent == AskIntent.GENERAL_RESEARCH and not plan.deterministic_answer
            )

            general_correct += int(correct_general)

        if not (intent_ok and area_ok and route_ok):
            failures.append(
                (
                    case,
                    plan,
                )
            )

    total = len(CASES)

    print("===== PRODUCTION HOLDOUT V4 =====")
    print(f"cases={total}")
    print(f"intent_accuracy={intent_correct / total:.3f}")
    print(f"area_accuracy={area_correct / total:.3f}")
    print(f"routing_accuracy={routing_correct / total:.3f}")

    print()
    print("===== SAFETY =====")
    print(f"safety_cases={safety_total}")
    print(f"causal_safety_recall={safety_correct / safety_total:.3f}")
    print(f"dangerous_misroute_rate={dangerous_misroutes / safety_total:.3f}")

    print()
    print("===== GENERAL RESEARCH =====")
    print(f"general_cases={general_total}")
    print(f"general_research_accuracy={general_correct / general_total:.3f}")

    print()
    print("===== ROUTER LATENCY =====")
    print(f"samples={len(latencies)}")
    print(f"p50_ms={median(latencies):.2f}")
    print(f"p95_ms={percentile(latencies, 0.95):.2f}")
    print(f"p99_ms={percentile(latencies, 0.99):.2f}")

    print()
    print("===== CONFUSION =====")

    if not confusion:
        print("none")

    for (
        expected,
        actual,
    ), count in confusion.most_common():
        print(f"{expected} -> {actual}: {count}")

    print()
    print("===== FAILURES =====")

    for case, plan in failures:
        print(f"question={case.question!r}")
        print(f"  expected_intent={case.intent.value}")
        print(f"  actual_intent={plan.intent.value}")
        print(f"  expected_area={case.area_fips}")
        print(f"  actual_area={plan.area_fips}")
        print(f"  expected_deterministic={case.deterministic}")
        print(f"  actual_deterministic={plan.deterministic_answer}")
        print()

    print(f"failures={len(failures)}")


if __name__ == "__main__":
    main()
