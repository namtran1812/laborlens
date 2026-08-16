from __future__ import annotations

from statistics import median

from laborlens.evaluation.assistant_benchmark import (
    run_benchmark,
)


def main() -> None:
    results = run_benchmark()

    planner = sum(result.planner_correct for result in results)

    deterministic = sum(result.deterministic_correct for result in results)

    area = sum(result.area_correct for result in results)

    guard = sum(result.guard_valid for result in results)

    latencies = [result.latency_ms for result in results]

    total = len(results)

    print(f"cases={total}")
    print(f"planner_accuracy={planner / total:.3f}")
    print(f"routing_accuracy={deterministic / total:.3f}")
    print(f"area_accuracy={area / total:.3f}")
    print(f"guard_pass_rate={guard / total:.3f}")
    print(f"latency_p50_ms={median(latencies):.2f}")
    print(f"latency_max_ms={max(latencies):.2f}")

    print()

    for result in results:
        print(
            f"{result.name}\t"
            f"planner={result.planner_correct}\t"
            f"route={result.deterministic_correct}\t"
            f"area={result.area_correct}\t"
            f"guard={result.guard_valid}\t"
            f"latency_ms={result.latency_ms:.2f}"
        )


if __name__ == "__main__":
    main()
