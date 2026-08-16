from __future__ import annotations

import json
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter

from benchmarks.grounding_v1 import CASES

URL = "http://localhost:8001/ask"

START_DATE = "2024-06-01"
AS_OF = "2024-09-01"


def percentile(
    values: list[float],
    q: float,
) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * q)
    return ordered[index]


def ask(
    question: str,
    area: str | None,
) -> tuple[dict, float]:
    payload = {
        "question": question,
        "start_date": START_DATE,
        "as_of": AS_OF,
        "industry_level": 6,
        "context_limit": 5,
    }

    if area is not None:
        payload["area"] = area

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    started = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=120,
    ) as response:
        result = json.load(response)

    elapsed_ms = (time.perf_counter() - started) * 1000.0

    return result, elapsed_ms


def contains_any(
    text: str,
    phrases: tuple[str, ...],
) -> bool:
    lowered = text.lower()

    return any(phrase in lowered for phrase in phrases)


def main() -> None:
    #
    # Warm the local model/API. Do not include this request
    # in latency measurements.
    #
    try:
        ask(
            "Give me a careful interpretation of this episode.",
            None,
        )
    except Exception as exc:
        raise SystemExit(
            f"Could not warm /ask. Make sure the API and local model are running. Error: {exc}"
        ) from exc

    results = []
    failures = []
    modes = Counter()
    models = Counter()

    request_success = 0
    generation_success = 0
    guard_pass = 0
    unsupported_causal = 0
    numeric_misrepresentation = 0
    provenance_coverage = 0

    ai_latencies = []
    all_latencies = []

    for case in CASES:
        try:
            response, latency_ms = ask(
                case.question,
                case.area,
            )
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            failures.append(
                (
                    case.name,
                    (f"request failure: {exc}; response_body={body!r}"),
                )
            )
            continue
        except (
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            failures.append(
                (
                    case.name,
                    f"request failure: {exc}",
                )
            )
            continue

        all_latencies.append(latency_ms)

        answer = str(
            response.get(
                "answer",
                "",
            )
        )

        mode = str(
            response.get(
                "mode",
                "",
            )
        )

        model = str(
            response.get(
                "model",
                "",
            )
        )

        sources = response.get(
            "sources",
            [],
        )

        caveat = str(
            response.get(
                "caveat",
                "",
            )
        )

        modes[mode] += 1
        models[model] += 1

        success = bool(answer.strip())

        request_success += int(success)
        generation_success += int(success and mode == "local-ai")

        is_ai = mode == "local-ai"

        if is_ai:
            ai_latencies.append(latency_ms)

        #
        # Production guard outcome is inferred from whether an AI
        # response survives as local-ai. Deterministic responses are
        # already inside the trusted deterministic path.
        #
        guarded = mode in {
            "local-ai",
            "deterministic-research",
        }

        guard_pass += int(guarded)

        #
        # High-level independent smoke checks. These are intentionally
        # conservative and do not replace answer_guard.py.
        #
        causal_violation = contains_any(
            answer,
            (
                "caused the",
                "caused this",
                "was caused by",
                "responsible for the",
                "the reason for",
                "the reason florida",
                "drove the contraction",
                "drove the weakness",
            ),
        ) and not contains_any(
            answer,
            (
                "does not establish",
                "cannot establish",
                "cannot conclude",
                "not enough evidence",
                "does not show",
                "does not prove",
                "cannot determine",
            ),
        )

        unsupported_causal += int(causal_violation)

        numeric_violation = case.numeric_risk and contains_any(
            answer,
            (
                "payems fell 0.85%",
                "payroll employment fell 0.85%",
                "employment fell 66.7%",
                "66.7% decline",
                "66.7 percent decline",
            ),
        )

        numeric_misrepresentation += int(numeric_violation)

        #
        # For cases where QCEW provenance matters, require the returned
        # evidence surface to contain an explicit QCEW source.
        #
        provenance_ok = True

        combined_provenance = (
            answer + " " + caveat + " " + " ".join(str(source) for source in sources)
        )

        if case.expect_qcew:
            provenance_ok = "qcew" in combined_provenance.lower()

        if case.expect_point_in_time:
            combined = combined_provenance.lower()

            provenance_ok = provenance_ok and contains_any(
                combined,
                (
                    "2024-09-01",
                    "2024-06-05",
                    "release",
                    "released",
                    "as-of",
                    "as of",
                    "vintage",
                    "historical information",
                ),
            )

        provenance_coverage += int(provenance_ok)

        expected_mode_ok = (
            mode == "local-ai" if case.expect_ai else mode == "deterministic-research"
        )

        #
        # Grounding correctness is independent of which safe
        # production route answered the question. Deterministic
        # answers are often preferable when the verified research
        # engine can answer directly.
        #
        case_ok = (
            success and guarded and not causal_violation and not numeric_violation and provenance_ok
        )

        results.append(
            {
                "name": case.name,
                "mode": mode,
                "model": model,
                "latency_ms": latency_ms,
                "success": success,
                "guarded": guarded,
                "causal_violation": causal_violation,
                "numeric_violation": numeric_violation,
                "provenance_ok": provenance_ok,
                "expected_mode_ok": expected_mode_ok,
                "answer": answer,
            }
        )

        if not case_ok:
            failures.append(
                (
                    case.name,
                    {
                        "mode": mode,
                        "model": model,
                        "causal_violation": causal_violation,
                        "numeric_violation": numeric_violation,
                        "provenance_ok": provenance_ok,
                        "expected_mode_ok": expected_mode_ok,
                        "answer": answer,
                    },
                )
            )

    total = len(CASES)

    print("===== GROUNDING V1 =====")
    print(f"cases={total}")
    print(f"request_success_rate={request_success / total:.3f}")
    print(f"ai_generation_rate={generation_success / total:.3f}")
    print(f"answer_guard_pass_rate={guard_pass / total:.3f}")
    print(f"unsupported_causal_assertion_rate={unsupported_causal / total:.3f}")
    print(f"numeric_misrepresentation_rate={numeric_misrepresentation / total:.3f}")
    print(f"provenance_coverage_rate={provenance_coverage / total:.3f}")

    print()
    print("===== MODES =====")

    for mode, count in modes.most_common():
        print(f"{mode}={count}")

    print()
    print("===== MODELS =====")

    for model, count in models.most_common():
        print(f"{model}={count}")

    print()
    print("===== END-TO-END LATENCY =====")

    if all_latencies:
        print(f"p50_ms={statistics.median(all_latencies):.2f}")
        print(f"p95_ms={percentile(all_latencies, 0.95):.2f}")
        print(f"p99_ms={percentile(all_latencies, 0.99):.2f}")

    print()
    print("===== AI GENERATION LATENCY =====")

    if ai_latencies:
        print(f"samples={len(ai_latencies)}")
        print(f"p50_ms={statistics.median(ai_latencies):.2f}")
        print(f"p95_ms={percentile(ai_latencies, 0.95):.2f}")
    else:
        print("samples=0")

    print()
    print("===== FAILURES =====")

    for name, failure in failures:
        print()
        print(f"case={name!r}")

        if isinstance(
            failure,
            dict,
        ):
            for key, value in failure.items():
                print(f"  {key}={value!r}")
        else:
            print(f"  {failure}")

    print()
    print(f"failures={len(failures)}")


if __name__ == "__main__":
    main()
