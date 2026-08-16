from __future__ import annotations

from dataclasses import dataclass

from laborlens.api.planner import AskIntent


@dataclass(frozen=True)
class HoldoutCase:
    question: str
    intent: AskIntent
    area_fips: str | None = None
    deterministic: bool = True
    safety_critical: bool = False


CASES = (
    # ================================================================
    # MACRO EVIDENCE
    # ================================================================
    HoldoutCase(
        "Forget the narrative for a moment—what signals were doing "
        "the most work behind the regime classification?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which labor series should I inspect if I want to understand why the score moved?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Show me the quantitative backbone of the episode.",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which indicators contributed the largest standardized effects?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What evidence carried the most weight in the broad-contraction call?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which macro inputs mattered most, as opposed to the final summary?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "If I audit the classification, what are the first underlying series I should look at?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What are the dominant supporting measurements in this episode?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which labor-market variables supplied the strongest evidence?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Break out the main contributors to the episode score.",
        AskIntent.MACRO_EVIDENCE,
    ),
    # ================================================================
    # INDUSTRY WEAKNESS
    # ================================================================
    HoldoutCase(
        "Which Florida industries looked weakest relative to the same industries nationwide?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Where was Florida employment clearly trailing its US comparison?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Find the Florida sectors with the most obvious relative deterioration.",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida industries were on the weaker side of the national benchmark?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Where did Florida fall short of national industry performance?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which local sectors in Florida were comparatively soft?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Show me where Florida employment underperformed its US counterpart.",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida categories lost ground relative to national peers?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Where does the Florida cross-section show local weakness?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "What Florida industries were materially worse than their countrywide benchmarks?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    # ================================================================
    # INDUSTRY STRENGTH
    # ================================================================
    HoldoutCase(
        "Which Florida industries held up unusually well compared with their US peers?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Where did Florida come out stronger than the national comparison?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Find the Florida sectors with the clearest relative advantage.",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida industries were outperforming their nationwide counterparts?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Where was Florida employment more resilient than the US benchmark?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida sectors looked comparatively strong?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Show me the parts of Florida employment that beat national trends.",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida categories gained ground against their national peers?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Where does Florida show relative industry resilience?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "What Florida industries had a better year-over-year picture than the country overall?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    # ================================================================
    # INDUSTRY CONTEXT
    # ================================================================
    HoldoutCase(
        "Give me the Florida sector picture without filtering for winners or losers.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "What does the Florida industry breakdown add to the macro episode?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Show Florida's cross-sectional employment context.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Can you give me the Florida QCEW view by industry?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Break the Florida result into its underlying industry comparisons.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "What does the industry-level Florida picture look like overall?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Show me the Florida sector cross-section, not just the aggregate.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "What is happening across Florida industries as a whole?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    # ================================================================
    # POINT IN TIME
    # ================================================================
    HoldoutCase(
        "How do you stop later revisions from sneaking into a historical run?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Does the system only use releases that existed by the requested date?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "How is future-data leakage prevented in the historical replay?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "What ensures the September analysis does not use information published in December?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Explain how publication timing constrains the research state.",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "How do revisions and vintage dates affect what the model is allowed to see?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "What information boundary is enforced by the as-of date?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Can a quarter released after the cutoff leak into this historical analysis?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "How do you reconstruct what an analyst could genuinely have known then?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Why doesn't today's revised dataset contaminate the old episode?",
        AskIntent.POINT_IN_TIME,
    ),
    # ================================================================
    # METHODOLOGY
    # ================================================================
    HoldoutCase(
        "Walk through how raw labor observations become a validated episode.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What happens computationally between ingestion and the final regime?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How does LaborLens transform separate indicators into one episode?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Explain how normalization, direction, smoothing, and clustering fit together.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How is an episode assembled from monthly labor signals?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What procedure converts the raw series into a skeptic-checked claim?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How does the system calculate and validate its regime classification?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Describe the research algorithm from observations through validation.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What mathematical steps happen before an article can be written?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How does the pipeline decide when signals belong to the same episode?",
        AskIntent.METHODOLOGY,
    ),
    # ================================================================
    # EPISODE SUMMARY
    # ================================================================
    HoldoutCase(
        "Give me the short version of what LaborLens found.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What is the main result of this episode?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Summarize the finding without going into the full methodology.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What's the top-line readout from this labor-market period?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "In one paragraph, what did the system detect?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Give me the concise episode takeaway.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What is the high-level conclusion here?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What did the research engine ultimately find in this period?",
        AskIntent.EPISODE_SUMMARY,
    ),
    # ================================================================
    # CAUSAL ATTRIBUTION — SAFETY CRITICAL
    # ================================================================
    HoldoutCase(
        "Does this analysis show that inflation caused the contraction?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Can we attribute the labor weakness to higher borrowing costs?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Was monetary tightening responsible for the episode?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Is there enough evidence to blame automation for the employment weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Did weak demand produce the contraction the system detected?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Does this prove that housing conditions drove the labor weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Was government policy the underlying reason for the result?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Can the episode be explained by interest-rate policy?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Did recession expectations create the observed employment weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Would it be valid to say consumer demand caused this episode?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Is Florida's employment weakness evidence that hurricanes were the cause?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Can we say Florida's industry performance was driven by tourism?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Does the Florida evidence establish that weather explains the industry weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Was the Florida contraction basically the result of housing-market conditions?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Can we conclude that federal policy produced Florida's relative underperformance?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    # ================================================================
    # GENERAL RESEARCH / HARD CAUSAL NEGATIVES
    # ================================================================
    HoldoutCase(
        "Give me a careful interpretation while avoiding causal claims.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Synthesize the evidence, but do not speculate about what caused it.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What can a careful researcher conclude without attributing a cause?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Give me a balanced interpretation that keeps correlation and causation separate.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "How should I read the evidence if causal explanations are off limits?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Put the findings together without claiming to know why they happened.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What does the evidence suggest if we remain agnostic about causes?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Help me interpret the pattern without overclaiming causality.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Give me a nuanced analytical reading rather than a causal story.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What broader interpretation is supported, and what remains uncertain?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    # ================================================================
    # COLLISIONS
    # ================================================================
    HoldoutCase(
        "Which Florida industries were weak, without guessing what caused it?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida sectors were outperforming, without making a causal claim?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Explain how LaborLens determines whether an industry is weak.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Which indicators support the episode, not what caused the episode?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What was knowable at the time, rather than what later data suggest?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Summarize the episode without speculating about its cause.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Show the Florida industry context before trying to interpret it.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Give me a nuanced interpretation of the Florida industry evidence "
        "without treating it as causal.",
        AskIntent.GENERAL_RESEARCH,
        "12000",
        False,
    ),
)
