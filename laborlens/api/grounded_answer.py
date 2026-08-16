from __future__ import annotations

from laborlens.api.assistant import AssistantAnswer
from laborlens.api.planner import (
    AskIntent,
    AskPlan,
)
from laborlens.research.research_bundle import (
    ResearchBundle,
)


def _macro_sources(
    bundle: ResearchBundle,
) -> tuple[str, ...]:
    return tuple(
        (f"{item.series_id} standardized contribution {item.contribution:.3f}")
        for item in bundle.evidence.supporting
    )


def _qcew_source(
    *,
    context,
    claim,
) -> str:
    release = (
        f", released {context.data_release_date}" if context.data_release_date is not None else ""
    )

    return (
        f"QCEW {context.year} Q{context.quarter}"
        f"{release}: "
        f"{claim.industry_title}; "
        f"local YoY {claim.local_yoy_growth:.1f}%, "
        f"US YoY {claim.national_yoy_growth:.1f}%, "
        f"relative gap {claim.relative_gap:.1f} pp"
    )


def _industry_claims(
    bundle: ResearchBundle,
    *,
    weakness: bool | None,
) -> list:
    context = bundle.cross_sectional_context

    if context is None:
        return []

    if weakness is None:
        return list(context.claims)

    if weakness:
        allowed = {
            "local_contraction",
            "relative_underperformance",
        }
    else:
        allowed = {
            "local_outperformance",
            "relative_resilience",
        }

    return [item for item in context.claims if item.claim_type in allowed]


def deterministic_answer(
    *,
    plan: AskPlan,
    bundle: ResearchBundle,
) -> AssistantAnswer:
    context = bundle.cross_sectional_context
    used_qcew_claims: list = []

    if plan.needs_qcew and context is None:
        return AssistantAnswer(
            answer=(
                "The verified bundle does not contain "
                "QCEW context for the requested geography "
                "and historical information state."
            ),
            mode="deterministic-research",
            model="laborlens-rules",
            sources=_macro_sources(bundle),
            caveat=("No unsupported geographic or industry inference was generated."),
        )

    if plan.intent == AskIntent.CAUSAL_ATTRIBUTION:
        answer = (
            "LaborLens cannot establish the proposed causal "
            "explanation from the verified evidence in this "
            "research bundle. The system identifies statistical "
            "labor-market patterns and cross-sectional industry "
            "differences, but those observations do not determine "
            "why the changes occurred."
        )

        if context is not None:
            answer += (
                f" For {context.area_title}, the point-in-time "
                f"QCEW context uses {context.year} Q"
                f"{context.quarter}, released "
                f"{context.data_release_date}; those industry "
                "comparisons are contextual evidence, not "
                "causal evidence."
            )

    elif plan.intent == AskIntent.MACRO_EVIDENCE:
        evidence = sorted(
            bundle.evidence.supporting,
            key=lambda item: abs(item.contribution),
            reverse=True,
        )

        details = ", ".join((f"{item.series_id} ({item.contribution:.2f})") for item in evidence)

        answer = (
            "The strongest standardized supporting "
            f"signals were {details}. These values are "
            "standardized directional contributions, "
            "not percentage changes in the underlying "
            "economic series."
        )

    elif plan.intent in {
        AskIntent.INDUSTRY_WEAKNESS,
        AskIntent.INDUSTRY_STRENGTH,
        AskIntent.INDUSTRY_CONTEXT,
    }:
        weakness = None

        if plan.intent == AskIntent.INDUSTRY_WEAKNESS:
            weakness = True

        elif plan.intent == AskIntent.INDUSTRY_STRENGTH:
            weakness = False

        used_qcew_claims = _industry_claims(
            bundle,
            weakness=weakness,
        )

        if not used_qcew_claims:
            answer = (
                "No validated QCEW claims matching that "
                "question passed the configured materiality "
                "and skeptic checks."
            )
        else:
            period = f"{context.year} Q{context.quarter}"

            release = (
                f", released {context.data_release_date}"
                if context.data_release_date is not None
                else ""
            )

            observations = []

            for item in used_qcew_claims:
                observations.append(f"{item.industry_title}: {item.evidence_text}")

            answer = (
                f"For {context.area_title}, the latest "
                f"QCEW context available to this historical "
                f"information state is {period}{release}. " + " ".join(observations)
            )

    elif plan.intent == AskIntent.POINT_IN_TIME:
        if context is not None:
            answer = (
                "LaborLens reconstructs the macro episode "
                "using only FRED/ALFRED vintages available "
                "by the requested information date. For "
                "cross-sectional context, it selected "
                f"QCEW {context.year} Q{context.quarter}, "
                f"released {context.data_release_date}, "
                f"which was available by "
                f"{context.requested_as_of_date}. This "
                "prevents later quarterly data from leaking "
                "into the historical analysis."
            )
        else:
            answer = (
                "LaborLens reconstructs each macro episode "
                "from FRED/ALFRED observations whose "
                "historical vintages were available at the "
                "requested information date, preventing "
                "later revisions from leaking into the "
                "analysis."
            )

    elif plan.intent == AskIntent.METHODOLOGY:
        answer = (
            "LaborLens reconstructs historical FRED/ALFRED "
            "information states, normalizes labor indicators "
            "against rolling history, combines directional "
            "signals into a regime score, clusters adjacent "
            "claims into episodes, and runs deterministic "
            "evidence and skeptic checks. When geography is "
            "requested, QCEW comparisons are separately "
            "validated against national industry baselines."
        )

    else:
        answer = (
            f"{bundle.claim.headline}. The episode ran from "
            f"{bundle.episode.start_date} through "
            f"{bundle.episode.end_date}, with a peak regime "
            f"score of {bundle.peak_episode_score:.3f}. "
            f"The skeptic verdict was "
            f"{bundle.skeptic.verdict}."
        )

        if context is not None:
            answer += (
                f" Point-in-time QCEW context for "
                f"{context.area_title} uses "
                f"{context.year} Q{context.quarter}, "
                f"released {context.data_release_date}."
            )

    sources = list(_macro_sources(bundle))

    if context is not None and used_qcew_claims:
        sources.extend(
            _qcew_source(
                context=context,
                claim=item,
            )
            for item in used_qcew_claims
        )

    elif plan.intent == AskIntent.POINT_IN_TIME and context is not None:
        sources.append(
            f"QCEW {context.year} Q{context.quarter} release: {context.data_release_date}"
        )

    return AssistantAnswer(
        answer=answer,
        mode="deterministic-research",
        model="laborlens-rules",
        sources=tuple(sources),
        caveat=("Answer generated only from verified LaborLens research outputs."),
    )
