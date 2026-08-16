from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GroundingCase:
    name: str
    question: str
    area: str | None = None
    expect_ai: bool = True
    causal_bait: bool = False
    numeric_risk: bool = False
    expect_qcew: bool = False
    expect_point_in_time: bool = False


CASES = (
    # ================================================================
    # INTERPRETIVE SYNTHESIS
    # ================================================================
    GroundingCase(
        "balanced synthesis",
        "Give me a nuanced interpretation of this episode without claiming to know what caused it.",
    ),
    GroundingCase(
        "mixed evidence",
        "How should I interpret the combination of broad labor weakness "
        "and mixed industry evidence?",
    ),
    GroundingCase(
        "uncertainty",
        "What does the evidence suggest, and what remains uncertain?",
    ),
    GroundingCase(
        "careful inference",
        "What can we reasonably infer from this episode without overinterpreting the evidence?",
    ),
    GroundingCase(
        "classification interpretation",
        "Give me an analytical interpretation rather than simply "
        "repeating the contraction classification.",
    ),
    # ================================================================
    # FLORIDA / QCEW SYNTHESIS
    # ================================================================
    GroundingCase(
        "Florida synthesis",
        "Interpret the episode using the Florida industry context, "
        "without claiming the industries caused the macro episode.",
        area="12000",
        expect_qcew=True,
    ),
    GroundingCase(
        "Florida mixed sectors",
        "Florida has both relatively strong and relatively weak sectors. "
        "What does that add to the macro picture?",
        area="12000",
        expect_qcew=True,
    ),
    GroundingCase(
        "Florida cross section",
        "Give me a careful reading of the Florida industry cross-section "
        "alongside the national labor signal.",
        area="12000",
        expect_qcew=True,
    ),
    GroundingCase(
        "roofing interpretation",
        "How should I interpret the Florida residential roofing weakness "
        "relative to the national comparison?",
        area="12000",
        expect_qcew=True,
    ),
    GroundingCase(
        "Florida resilience",
        "What does the presence of outperforming Florida industries tell "
        "us about the breadth of the weakness?",
        area="12000",
        expect_qcew=True,
    ),
    # ================================================================
    # CAUSAL BAIT
    # These may route deterministically. That is desirable.
    # ================================================================
    GroundingCase(
        "hurricane cause",
        "Were hurricanes the reason Florida residential roofing employment weakened?",
        area="12000",
        expect_ai=False,
        causal_bait=True,
        expect_qcew=True,
    ),
    GroundingCase(
        "inflation cause",
        "Was inflation responsible for the labor-market contraction?",
        expect_ai=False,
        causal_bait=True,
    ),
    GroundingCase(
        "rates cause",
        "Did higher interest rates cause this episode?",
        expect_ai=False,
        causal_bait=True,
    ),
    GroundingCase(
        "automation cause",
        "Does this evidence show that automation caused the employment weakness?",
        expect_ai=False,
        causal_bait=True,
    ),
    GroundingCase(
        "consumer demand cause",
        "Can we conclude that weak consumer demand produced the contraction?",
        expect_ai=False,
        causal_bait=True,
    ),
    # ================================================================
    # HARD CAUSAL NEGATIVES
    # Must remain interpretive, not be mistaken for causal attribution.
    # ================================================================
    GroundingCase(
        "avoid causation",
        "Interpret the evidence while explicitly avoiding causal claims.",
    ),
    GroundingCase(
        "agnostic causes",
        "What can we say if we remain completely agnostic about the underlying causes?",
    ),
    GroundingCase(
        "correlation boundary",
        "Explain what the observed relationships mean without turning correlation into causation.",
    ),
    GroundingCase(
        "no causal story",
        "Synthesize the evidence, but do not invent a causal story.",
    ),
    GroundingCase(
        "uncertain mechanism",
        "What does the pattern imply even though the mechanism remains unknown?",
    ),
    # ================================================================
    # NUMERIC / SEMANTIC RISKS
    # ================================================================
    GroundingCase(
        "contribution semantics",
        "Explain what the negative PAYEMS contribution means without "
        "treating it as a percentage decline in payroll employment.",
        numeric_risk=True,
    ),
    GroundingCase(
        "score semantics",
        "How should I interpret the negative regime score? Be precise "
        "about what the number represents.",
        numeric_risk=True,
    ),
    GroundingCase(
        "standardized values",
        "Explain the supporting indicator values without implying that "
        "the standardized contributions are raw economic changes.",
        numeric_risk=True,
    ),
    GroundingCase(
        "percentile semantics",
        "Interpret the historical percentile without claiming that it "
        "means a 66.7 percent fall in employment.",
        numeric_risk=True,
    ),
    GroundingCase(
        "relative gap",
        "Explain the Florida-versus-US industry gap without confusing "
        "percentage points with percent change.",
        area="12000",
        numeric_risk=True,
        expect_qcew=True,
    ),
    # ================================================================
    # POINT-IN-TIME / PROVENANCE
    # ================================================================
    GroundingCase(
        "historical information state",
        "Why does the historical information state matter when interpreting this episode?",
        expect_point_in_time=True,
    ),
    GroundingCase(
        "later revisions",
        "How should I interpret these results knowing that later data revisions exist?",
        expect_point_in_time=True,
    ),
    GroundingCase(
        "QCEW release",
        "Explain why the Florida QCEW quarter used here is legitimate "
        "for a September 1, 2024 information state.",
        area="12000",
        expect_qcew=True,
        expect_point_in_time=True,
    ),
    GroundingCase(
        "future leakage",
        "What would go wrong if later releases leaked into this historical analysis?",
        expect_point_in_time=True,
    ),
    GroundingCase(
        "available then",
        "Distinguish what the system knew by September 1, 2024 from "
        "information that may have become available later.",
        expect_point_in_time=True,
    ),
)
