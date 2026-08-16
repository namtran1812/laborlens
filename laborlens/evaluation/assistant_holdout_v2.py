from __future__ import annotations

from dataclasses import dataclass

from laborlens.api.planner import (
    AskIntent,
    plan_question,
)


@dataclass(frozen=True)
class HoldoutV2Case:
    question: str
    intent: AskIntent
    area: str | None
    deterministic: bool


CASES: tuple[HoldoutV2Case, ...] = (
    # Macro evidence
    HoldoutV2Case(
        "I'm less interested in the headline — which underlying "
        "labor signals actually carried the episode?",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    HoldoutV2Case(
        "If you had to rank the evidence behind the contraction, what would come first?",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    HoldoutV2Case(
        "What parts of the macro data gave the model the strongest support?",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    HoldoutV2Case(
        "Which series were doing most of the work in this classification?",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    HoldoutV2Case(
        "Show me what is underneath the broad-contraction call.",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    HoldoutV2Case(
        "Which labor measures pushed the regime toward contraction?",
        AskIntent.MACRO_EVIDENCE,
        None,
        True,
    ),
    # Industry weakness
    HoldoutV2Case(
        "Florida looks mixed — where specifically was it falling behind comparable US industries?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Among Florida employers, where does the relative weakness show up?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "What parts of Florida's industry base were losing momentum versus the country?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Point me to the Florida sectors that compare poorly with their national benchmarks.",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Where is Florida on the wrong side of the national comparison?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Which Florida employment categories were materially softer than their US counterparts?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
        True,
    ),
    # Industry strength
    HoldoutV2Case(
        "The macro picture was soft, but where was Florida actually holding up well?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Which Florida sectors looked better than the corresponding national industries?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Where did Florida buck the weaker national trend?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Show me pockets of relative strength in Florida employment.",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Which Florida industries were comparatively resilient?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Where did Florida come out ahead of the US comparison?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
        True,
    ),
    # Industry context
    HoldoutV2Case(
        "Zoom in from the national picture and show me Florida by industry.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "What does the Florida cross-section add to the national story?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Give me the industry-level evidence for Florida rather than just the aggregate signal.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Can you break Florida down sector by sector?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "What's visible when we move from the macro episode to Florida QCEW?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
        True,
    ),
    # Point in time
    HoldoutV2Case(
        "Are you accidentally letting later revisions influence what "
        "the system supposedly knew in September?",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    HoldoutV2Case(
        "How can I tell this isn't using today's revised data to judge 2024?",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    HoldoutV2Case(
        "What stops December data from leaking into a September analysis?",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    HoldoutV2Case(
        "When you say 'as of September 1', what information is excluded?",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    HoldoutV2Case(
        "Does the historical replay respect when agencies actually published the data?",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    HoldoutV2Case(
        "Explain why the historical result isn't hindsight-biased.",
        AskIntent.POINT_IN_TIME,
        None,
        True,
    ),
    # Methodology
    HoldoutV2Case(
        "Suppose I gave you the raw labor series. What does LaborLens "
        "do to turn them into an episode?",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    HoldoutV2Case(
        "Walk through the machinery between observations and the final contraction label.",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    HoldoutV2Case(
        "How does the system decide that adjacent monthly signals belong to one episode?",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    HoldoutV2Case(
        "What happens mathematically before the skeptic sees a claim?",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    HoldoutV2Case(
        "How do normalization, smoothing, and clustering fit together?",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    HoldoutV2Case(
        "What's the sequence from incoming indicators to validated research?",
        AskIntent.METHODOLOGY,
        None,
        True,
    ),
    # Episode summary
    HoldoutV2Case(
        "I don't need all the details. What did the system ultimately find?",
        AskIntent.EPISODE_SUMMARY,
        None,
        True,
    ),
    HoldoutV2Case(
        "Give me the executive-summary version of the June episode.",
        AskIntent.EPISODE_SUMMARY,
        None,
        True,
    ),
    HoldoutV2Case(
        "In plain English, what happened here?",
        AskIntent.EPISODE_SUMMARY,
        None,
        True,
    ),
    HoldoutV2Case(
        "What's the one-paragraph readout of this episode?",
        AskIntent.EPISODE_SUMMARY,
        None,
        True,
    ),
    HoldoutV2Case(
        "Before we dig into causes, what did LaborLens actually detect?",
        AskIntent.EPISODE_SUMMARY,
        None,
        True,
    ),
    # Causal attribution — must NEVER reach free synthesis.
    HoldoutV2Case(
        "Is the roofing weakness basically a hurricane story?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Should I interpret this as evidence that high rates caused the labor slowdown?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Can we reasonably pin the contraction on inflation?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Would it be fair to say monetary tightening drove the result?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Is automation what explains the weakness we're seeing?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Does this prove weak demand was behind the employment deterioration?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Can I conclude from this that housing conditions explain Florida roofing employment?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
    ),
    HoldoutV2Case(
        "Was government policy the underlying driver here?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Did uncertainty create the broad contraction signal?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
    ),
    HoldoutV2Case(
        "Is there enough evidence to say tourism caused the Florida weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
    ),
    # Genuine interpretive synthesis
    HoldoutV2Case(
        "Give me a cautious interpretation that connects the pieces "
        "without pretending we know the cause.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutV2Case(
        "How would a careful researcher read these mixed signals?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutV2Case(
        "Put the national evidence and Florida cross-section into a "
        "coherent interpretation without overclaiming.",
        AskIntent.GENERAL_RESEARCH,
        "12000",
        False,
    ),
    HoldoutV2Case(
        "What is the most defensible interpretation of the evidence as a whole?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutV2Case(
        "Help me reason about the combination of macro weakness and mixed Florida sectors.",
        AskIntent.GENERAL_RESEARCH,
        "12000",
        False,
    ),
    HoldoutV2Case(
        "Synthesize the story, but keep correlation and causation separate.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
)


@dataclass(frozen=True)
class HoldoutV2Result:
    total: int
    intent_correct: int
    area_correct: int
    routing_correct: int
    causal_total: int
    causal_correct: int


def evaluate_holdout_v2() -> tuple[
    HoldoutV2Result,
    list[tuple[HoldoutV2Case, object]],
]:
    intent_correct = 0
    area_correct = 0
    routing_correct = 0
    causal_total = 0
    causal_correct = 0
    failures = []

    for case in CASES:
        plan = plan_question(case.question)

        intent_ok = plan.intent == case.intent
        area_ok = plan.area_fips == case.area
        routing_ok = plan.deterministic_answer == case.deterministic

        intent_correct += int(intent_ok)
        area_correct += int(area_ok)
        routing_correct += int(routing_ok)

        if case.intent == AskIntent.CAUSAL_ATTRIBUTION:
            causal_total += 1
            causal_correct += int(intent_ok and routing_ok)

        if not (intent_ok and area_ok and routing_ok):
            failures.append(
                (
                    case,
                    plan,
                )
            )

    return (
        HoldoutV2Result(
            total=len(CASES),
            intent_correct=intent_correct,
            area_correct=area_correct,
            routing_correct=routing_correct,
            causal_total=causal_total,
            causal_correct=causal_correct,
        ),
        failures,
    )
