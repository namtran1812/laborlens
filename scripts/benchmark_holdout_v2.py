from laborlens.evaluation.assistant_holdout_v2 import (
    evaluate_holdout_v2,
)


def main() -> None:
    result, failures = evaluate_holdout_v2()

    print("===== HOLDOUT V2 =====")
    print(f"cases={result.total}")
    print(f"intent_accuracy={result.intent_correct / result.total:.3f}")
    print(f"area_accuracy={result.area_correct / result.total:.3f}")
    print(f"routing_accuracy={result.routing_correct / result.total:.3f}")

    if result.causal_total:
        print(f"causal_routing_accuracy={result.causal_correct / result.causal_total:.3f}")

    print(f"failures={len(failures)}")

    print()
    print("===== FAILURES =====")

    for case, plan in failures:
        print(f"question={case.question!r}")
        print(f"  expected_intent={case.intent}")
        print(f"  actual_intent={plan.intent}")
        print(f"  expected_area={case.area}")
        print(f"  actual_area={plan.area_fips}")
        print(f"  expected_deterministic={case.deterministic}")
        print(f"  actual_deterministic={plan.deterministic_answer}")
        print()


if __name__ == "__main__":
    main()
