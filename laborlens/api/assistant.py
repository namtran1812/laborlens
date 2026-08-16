from __future__ import annotations

from dataclasses import dataclass

import httpx

from laborlens.api.answer_guard import validate_ai_answer
from laborlens.config import Settings
from laborlens.research.research_bundle import ResearchBundle


@dataclass(frozen=True)
class AssistantAnswer:
    answer: str
    mode: str
    model: str
    sources: tuple[str, ...]
    caveat: str


def _bundle_context(
    bundle: ResearchBundle,
) -> str:
    support = "\n".join(
        (f"- {item.series_id}: {item.contribution:.3f}") for item in bundle.evidence.supporting
    )

    opposing = "\n".join(
        (f"- {item.series_id}: {item.contribution:.3f}") for item in bundle.evidence.opposing
    )

    context = bundle.cross_sectional_context

    if context is None:
        qcew = "none"
    else:
        qcew_claims = "\n".join(
            (
                f"- {item.claim_type}: "
                f"{item.industry_title}; "
                f"local_yoy={item.local_yoy_growth:.1f}%; "
                f"national_yoy="
                f"{item.national_yoy_growth:.1f}%; "
                f"relative_gap={item.relative_gap:.1f}pp; "
                f"skeptic={item.skeptic_verdict}"
            )
            for item in context.claims
        )

        qcew = (
            f"Area: {context.area_title}\n"
            f"Period: {context.year} Q"
            f"{context.quarter}\n"
            f"Context mode: {context.context_mode}\n"
            f"Release date: "
            f"{context.data_release_date}\n"
            f"Requested as-of: "
            f"{context.requested_as_of_date}\n"
            f"Validated claims:\n"
            f"{qcew_claims or 'none'}"
        )

    return f"""
Episode:
{bundle.episode.start_date} through {bundle.episode.end_date}

Claim:
{bundle.claim.headline}

Claim type:
{bundle.episode.claim_type}

Mean episode score:
{bundle.mean_episode_score:.3f}

Peak episode score:
{bundle.peak_episode_score:.3f}

Skeptic verdict:
{bundle.skeptic.verdict}

Skeptic score:
{bundle.skeptic.score:.3f}

Supporting macro evidence:
{support or "none"}

Opposing macro evidence:
{opposing or "none"}

Historical percentile:
{bundle.historical_percentile:.3f}

QCEW cross-sectional context:
{qcew}

Rules:
- Use only verified values above.
- Do not invent causes.
- Do not invent statistics.
- Do not infer sector causation from cross-sectional context.
- Distinguish standardized contributions from natural-unit changes.
- Respect the QCEW release date and requested as-of date.
- State uncertainty and limitations.
""".strip()


def ollama_answer(
    *,
    question: str,
    bundle: ResearchBundle,
    settings: Settings,
) -> AssistantAnswer:
    prompt = f"""
You are the LaborLens research assistant.

Your job is LANGUAGE SYNTHESIS ONLY.

All economic facts must come from the verified context below.
The deterministic LaborLens research engine has already
performed the calculations and validation.

STRICT RULES

1. Use only facts explicitly present in VERIFIED CONTEXT.
2. Never invent causes, mechanisms, events, policy explanations,
   industry drivers, or external facts.
3. Never describe standardized macro contributions as raw
   economic values or percentage changes.
4. PAYEMS, UNRATE, ICSA, JTSHIR, and similar numbers under
   macro evidence are STANDARDIZED CONTRIBUTIONS.
5. Do not infer that a national macro contraction means
   employment contracted in Florida.
6. QCEW claims are cross-sectional industry comparisons.
   They provide context; they do not explain the macro episode.
7. Do not generalize from listed industries to the entire
   Florida economy.
8. Do not use causal language such as "caused by",
   "driven by", "because of", or "influenced by" unless
   VERIFIED CONTEXT explicitly establishes that mechanism.
9. If the user asks for an unsupported cause, say that the
   verified evidence cannot establish it.
10. Respect the historical information boundary.
11. If QCEW evidence is mixed, acknowledge both weakness
    and strength.
12. Do not introduce statistics absent from the context.
13. Distinguish:
      - national macro evidence,
      - Florida QCEW context,
      - interpretation.
14. Prefer "the evidence shows" or "is consistent with"
    over unsupported explanations.

VERIFIED CONTEXT
----------------
{_bundle_context(bundle)}

USER QUESTION
-------------
{question}

Use this structure:

Direct answer:
<1-2 sentences>

Evidence:
<only verified macro and QCEW facts>

Interpretation:
<what the evidence supports without causal inference>

Limitations:
<what the evidence does not establish>
""".strip()

    response = httpx.post(
        f"{settings.ollama_host.rstrip('/')}/api/generate",
        json={
            "model": settings.laborlens_model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.0,
            },
        },
        timeout=90.0,
    )

    response.raise_for_status()

    answer = (
        response.json()
        .get(
            "response",
            "",
        )
        .strip()
    )

    if not answer:
        raise RuntimeError("Ollama returned an empty assistant response")

    guard = validate_ai_answer(answer)

    if not guard.valid:
        raise RuntimeError("AI answer failed grounding validation: " + "; ".join(guard.violations))

    sources: list[str] = [item.series_id for item in bundle.evidence.supporting]

    context = bundle.cross_sectional_context

    if context is not None:
        release = (
            f", released {context.data_release_date}"
            if context.data_release_date is not None
            else ""
        )

        sources.extend(
            (
                f"QCEW {context.year} "
                f"Q{context.quarter}"
                f"{release}: "
                f"{item.industry_title}; "
                f"local YoY "
                f"{item.local_yoy_growth:.1f}%, "
                f"US YoY "
                f"{item.national_yoy_growth:.1f}%, "
                f"relative gap "
                f"{item.relative_gap:.1f} pp"
            )
            for item in context.claims
        )

    return AssistantAnswer(
        answer=answer,
        mode="local-ai",
        model=settings.laborlens_model,
        sources=tuple(sources),
        caveat=(
            "AI explanation generated only from a "
            "deterministically verified LaborLens "
            "research bundle. Cross-sectional QCEW "
            "context does not establish causation."
        ),
    )
