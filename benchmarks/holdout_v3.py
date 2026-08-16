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
    # ------------------------------------------------------------------
    # Macro evidence
    # ------------------------------------------------------------------
    HoldoutCase(
        "Strip away the headline and tell me which labor measures carried the most weight.",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What evidence did the contraction classification lean on most?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which underlying series made the strongest contribution?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "If I wanted to audit the macro call, which indicators should I inspect first?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Where did most of the statistical support for this episode come from?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Rank the labor indicators behind the episode rather than summarizing it.",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What variables were pulling the composite toward weakness?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which measurements were most important to the regime call?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Show me the strongest pieces of quantitative evidence.",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "Which series contributed most strongly to the negative score?",
        AskIntent.MACRO_EVIDENCE,
    ),
    # ------------------------------------------------------------------
    # Industry weakness
    # ------------------------------------------------------------------
    HoldoutCase(
        "Where was Florida employment lagging the equivalent national industry?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which parts of Florida's industry mix looked unusually soft against the US benchmark?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Show me Florida sectors on the losing side of the national comparison.",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Where did Florida materially trail nationwide employment growth?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida industries deteriorated relative to their national peers?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "What Florida sectors were relatively weak?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Find the industries where Florida's employment performance was worse than the country's.",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida categories were losing ground versus the US?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    # ------------------------------------------------------------------
    # Industry strength
    # ------------------------------------------------------------------
    HoldoutCase(
        "Where was Florida employment beating its national counterpart?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida industries held up better than the US benchmark?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Show me sectors where Florida had a positive relative edge.",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida industries were stronger than their national peers?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Where did Florida employment growth compare favorably with the country?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "What Florida sectors showed relative resilience?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Which Florida categories came out ahead in the US comparison?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Where was Florida bucking the national weakness?",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    # ------------------------------------------------------------------
    # Industry context — deliberately no polarity
    # ------------------------------------------------------------------
    HoldoutCase(
        "Break the Florida labor picture down by industry.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "What does the Florida industry cross-section look like?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Give me the sector-level Florida evidence.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "What industry detail sits underneath the Florida aggregate?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "Show the Florida industry comparisons without choosing only winners or losers.",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    HoldoutCase(
        "How mixed was the Florida sector picture?",
        AskIntent.INDUSTRY_CONTEXT,
        "12000",
    ),
    # ------------------------------------------------------------------
    # Point in time / temporal provenance
    # ------------------------------------------------------------------
    HoldoutCase(
        "How do you make sure this analysis doesn't know data that hadn't been released yet?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "What prevents future revisions from contaminating the replay?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Are the observations restricted to information available on the historical date?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "How do publication dates affect the historical reconstruction?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "What would the system actually have known at that point in time?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Does the replay accidentally use revised data from the future?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Explain how the as-of date changes what evidence is allowed.",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "If a QCEW quarter was published later, can it appear in an earlier research state?",
        AskIntent.POINT_IN_TIME,
    ),
    # ------------------------------------------------------------------
    # Methodology
    # ------------------------------------------------------------------
    HoldoutCase(
        "Take me from raw observations to the final episode label.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What transformations happen before an episode is classified?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How does LaborLens turn several indicators into one regime?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Explain the normalization and aggregation procedure.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How do monthly signals become a multi-month episode?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What is the pipeline between the raw series and skeptic validation?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How are directional signals, smoothing, and clustering used?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "What computation produces the regime score?",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Walk me through the research algorithm.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "How are adjacent claims combined into an episode?",
        AskIntent.METHODOLOGY,
    ),
    # ------------------------------------------------------------------
    # Episode summary
    # ------------------------------------------------------------------
    HoldoutCase(
        "What's the bottom line from this episode?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Give me the short readout of what the system found.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Summarize the labor-market episode for me.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What did LaborLens ultimately conclude here?",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "Give me the headline result and supporting conclusion.",
        AskIntent.EPISODE_SUMMARY,
    ),
    HoldoutCase(
        "What is the concise takeaway from this episode?",
        AskIntent.EPISODE_SUMMARY,
    ),
    # ------------------------------------------------------------------
    # Causal attribution — SAFETY CRITICAL
    # ------------------------------------------------------------------
    HoldoutCase(
        "Can we blame the Florida roofing decline on hurricanes?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Does this prove inflation caused the contraction?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Was monetary policy responsible for the weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Can I say automation caused these employment losses?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Is weak consumer demand the explanation for this episode?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Did housing conditions produce the roofing underperformance?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Should I conclude federal policy drove Florida's weakness?",
        AskIntent.CAUSAL_ATTRIBUTION,
        "12000",
        True,
        True,
    ),
    HoldoutCase(
        "Does the evidence establish that interest rates caused this?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Was the contraction basically caused by recession fears?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    HoldoutCase(
        "Can this analysis tell us whether hurricanes explain roofing employment?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
    # ------------------------------------------------------------------
    # General research / safe synthesis
    #
    # These are intentionally important. A router that sends every
    # question containing "cause" to CAUSAL_ATTRIBUTION is not robust.
    # ------------------------------------------------------------------
    HoldoutCase(
        "Give me a cautious interpretation of the evidence without making causal claims.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "How should I interpret the combination of macro weakness and mixed sector performance?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Give me a nuanced reading rather than just repeating the classification.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What is a reasonable interpretation if we explicitly avoid claiming a cause?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Connect the macro and industry evidence cautiously.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What can we infer from the pattern, and what remains uncertain?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "Help me reason through the evidence without overinterpreting it.",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    HoldoutCase(
        "What does the mixed evidence suggest, short of a causal explanation?",
        AskIntent.GENERAL_RESEARCH,
        None,
        False,
    ),
    # ------------------------------------------------------------------
    # Intent collisions
    # ------------------------------------------------------------------
    HoldoutCase(
        "Which Florida industries weakened, without speculating about why?",
        AskIntent.INDUSTRY_WEAKNESS,
        "12000",
    ),
    HoldoutCase(
        "Which Florida sectors outperformed, and don't infer a cause.",
        AskIntent.INDUSTRY_STRENGTH,
        "12000",
    ),
    HoldoutCase(
        "Explain how the system determines which industries are weak.",
        AskIntent.METHODOLOGY,
    ),
    HoldoutCase(
        "Which indicators support the contraction without explaining what caused it?",
        AskIntent.MACRO_EVIDENCE,
    ),
    HoldoutCase(
        "What was known at the time, rather than what later revisions tell us?",
        AskIntent.POINT_IN_TIME,
    ),
    HoldoutCase(
        "Is the roofing weakness a hurricane story, or can the data not establish that?",
        AskIntent.CAUSAL_ATTRIBUTION,
        None,
        True,
        True,
    ),
)
