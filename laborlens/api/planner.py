from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class AskIntent(StrEnum):
    CAUSAL_ATTRIBUTION = "causal_attribution"
    EPISODE_SUMMARY = "episode_summary"
    MACRO_EVIDENCE = "macro_evidence"
    INDUSTRY_WEAKNESS = "industry_weakness"
    INDUSTRY_STRENGTH = "industry_strength"
    INDUSTRY_CONTEXT = "industry_context"
    POINT_IN_TIME = "point_in_time"
    METHODOLOGY = "methodology"
    GENERAL_RESEARCH = "general_research"


AREA_ALIASES: dict[str, str] = {
    "florida": "12000",
}


@dataclass(frozen=True)
class AskPlan:
    intent: AskIntent
    area_fips: str | None
    needs_qcew: bool
    needs_macro: bool
    deterministic_answer: bool


def _normalize(
    text: str,
) -> str:
    return " ".join(
        re.findall(
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            text.lower(),
        )
    )


def _resolve_area(
    question: str,
    explicit_area: str | None,
) -> str | None:
    if explicit_area:
        return explicit_area

    normalized = _normalize(question)

    for name, area_fips in AREA_ALIASES.items():
        if re.search(
            rf"\b{re.escape(name)}\b",
            normalized,
        ):
            return area_fips

    return None


def _matches(
    text: str,
    patterns: tuple[str, ...],
) -> int:
    return sum(
        1
        for pattern in patterns
        if re.search(
            pattern,
            text,
        )
    )


CAUSAL_PATTERNS = (
    r"\bcaus(?:e|ed|ing|al)\b",
    r"\breason\b",
    r"\bresponsib(?:le|ility)\b",
    r"\battribut(?:e|ed|ion)\b",
    r"\bblam(?:e|ed|ing)\b",
    r"\bproduc(?:e|ed|ing)\b",
    r"\bcreat(?:e|ed|ing)\b",
    r"\bdriv(?:e|en|ing)\b",
    r"\bdrove\b",
    r"\bled to\b",
    r"\bresult(?:ed)? from\b",
    r"\bbecause of\b",
    r"\bdue to\b",
)

INTERPRETIVE_PATTERNS = (
    r"\binterpret(?:ation|ive|ing)?\b",
    r"\bnuanced\b",
    r"\bsynthesi[sz]e\b",
    r"\bsynthesis\b",
    r"\bput .* together\b",
    r"\bbalanced interpretation\b",
    r"\bcoherent .* narrative\b",
    r"\bwhat .* suggest\b",
    r"\bwhat .* imply\b",
)

POINT_IN_TIME_PATTERNS = (
    r"\bhistorical data release(?:s)?\b",
    r"\bdata release(?:s)?\b",
    r"\bpoint-in-time\b",
    r"\bpoint in time\b",
    r"\bvintage(?:s)?\b",
    r"\bhindsight\b",
    r"\blookahead\b",
    r"\blook-ahead\b",
    r"\bfuture information\b",
    r"\bfuture observations\b",
    r"\brevised data\b",
    r"\bpublication date(?:s)?\b",
    r"\brelease date(?:s)?\b",
    r"\bhistorical data cutoff\b",
    r"\bas-of date\b",
    r"\bavailable then\b",
    r"\bavailable at the time\b",
    r"\bknown then\b",
    r"\bknown at the time\b",
    r"\bhistorical information state(?:s)?\b",
    r"\bpublication schedule(?:s)?\b",
)

METHODOLOGY_PATTERNS = (
    r"\bhow does laborlens work\b",
    r"\bhow .* analy[sz](?:e|es|ed|ing)? .* episode(?:s)?\b",
    r"\bwhat steps .* classification\b",
    r"\bmethodolog(?:y|ical)\b",
    r"\banalytical procedure\b",
    r"\bscoring procedure\b",
    r"\bresearch engine\b",
    r"\bresearch pipeline\b",
    r"\banalytical workflow\b",
    r"\bworkflow\b",
    r"\bprocedure\b",
    r"\bhow .* calculated\b",
    r"\bhow .* detected\b",
    r"\bhow .* combined\b",
    r"\bhow .* transform\b",
    r"\bhow .* converted\b",
    r"\bhow .* analy[sz]\b",
    r"\bhow .* validate\b",
    r"\bwhat steps\b",
)

INDUSTRY_PATTERNS = (
    r"\bindustr(?:y|ies)\b",
    r"\bsector(?:s)?\b",
    r"\bsectoral\b",
    r"\bcross-sectional\b",
    r"\bemployment\b",
)

WEAKNESS_PATTERNS = (
    r"\bweak(?:er|est|ness|ening|ened)?\b",
    r"\bdeclin(?:e|ed|ing)\b",
    r"\bcontract(?:ion|ing|ed)?\b",
    r"\bunderperform(?:ance|ed|ing)?\b",
    r"\blag(?:ged|ging)?\b",
    r"\bworse\b",
    r"\bdeteriorat(?:e|ed|ion|ing)\b",
    r"\blosing ground\b",
    r"\bnegative relative gap(?:s)?\b",
)

STRENGTH_PATTERNS = (
    r"\bgrow(?:s|ing|th)? faster\b",
    r"\bpositive relative performance\b",
    r"\bstrong(?:er|est|ly)?\b",
    r"\bstrength\b",
    r"\boutperform(?:ance|ed|ing)?\b",
    r"\bresilien(?:t|ce)\b",
    r"\bbetter\b",
    r"\bgaining ground\b",
    r"\bbeat\b",
    r"\bpositive relative gap(?:s)?\b",
    r"\bheld up better\b",
)

COMPARISON_PATTERNS = (
    r"\bnation\b",
    r"\bnational\b",
    r"\bus\b",
    r"\bu s\b",
    r"\brelative\b",
    r"\bpeer(?:s)?\b",
    r"\bcounterpart(?:s)?\b",
    r"\bcompare\b",
    r"\bcomparison(?:s)?\b",
)

INDUSTRY_CONTEXT_PATTERNS = (
    r"\bacross .* industr(?:y|ies)\b",
    r"\bindustr(?:y|ies) .* context\b",
    r"\bindustry context\b",
    r"\bsector context\b",
    r"\bindustry breakdown\b",
    r"\bsector breakdown\b",
    r"\bindustry-level picture\b",
    r"\bsector-level view\b",
    r"\bcross-sectional .* picture\b",
    r"\bcross-sectional context\b",
    r"\bindustry comparisons\b",
    r"\bsector evidence\b",
    r"\bqcew\b",
)

MACRO_EVIDENCE_PATTERNS = (
    r"\bevidence .* support(?:ed|s|ing)?\b",
    r"\bsupport(?:ed|s|ing)? .* evidence\b",
    r"\bsignal(?:s)? .* support(?:ed|s|ing)?\b",
    r"\bsignal(?:s)? .* dominat(?:e|ed|es|ing)\b",
    r"\bdominant .* evidence\b",
    r"\bcontribut(?:e|ed|es|ing) .* regime score\b",
    r"\bcontribut(?:e|ed|es|ing|ion|ions) most\b",
    r"\bwhich indicator(?:s)?\b",
    r"\bindicator(?:s)? .* contribut",
    r"\bcontribution(?:s)? .* indicator",
    r"\bmacro evidence\b",
    r"\bmacro signal(?:s)?\b",
    r"\blabor indicator(?:s)?\b",
    r"\beconomic signal(?:s)?\b",
    r"\beconomic series\b",
    r"\bdata series\b",
    r"\bsupporting indicator(?:s)?\b",
    r"\bsupporting signal(?:s)?\b",
    r"\bstandardized contribution(?:s)?\b",
    r"\bindicator contribution(?:s)?\b",
    r"\bcontribution breakdown\b",
    r"\bevidence .* support\b",
    r"\bsupport .* classification\b",
    r"\bstrongest evidence\b",
    r"\bdominant .* signal(?:s)?\b",
    r"\bmost influential\b",
    r"\bbiggest effect\b",
    r"\blargest contribution(?:s)?\b",
    r"\bmattered most\b",
    r"\bmost important\b",
)

EPISODE_SUMMARY_PATTERNS = (
    r"\bexplain this episode\b",
    r"\bwhat was happening in the labor market\b",
    r"\bsummar(?:y|ize)\b",
    r"\bshort version\b",
    r"\boverview\b",
    r"\brecap\b",
    r"\bmain takeaway\b",
    r"\bhigh level\b",
    r"\bwhat happened\b",
    r"\bdescribe .* episode\b",
    r"\bwhat .* detect(?:ed)?\b",
)


def _industry_polarity(
    normalized: str,
) -> AskIntent | None:
    weakness_patterns = (
        r"\bweak(?:en(?:ing|ed)?|ness|er|est)?\b",
        r"\bunderperform(?:ed|ing|ance)?\b",
        r"\blag(?:ged|ging)?\b",
        r"\bfall(?:ing)? behind\b",
        r"\blosing ground\b",
        r"\bdeclin(?:e|ed|ing)\b",
        r"\bcontract(?:ed|ing|ion)?\b",
        r"\bdeteriorat(?:ed|ing|ion)?\b",
        r"\bworse\b",
        r"\bsofter\b",
        r"\bnegative relative\b",
    )

    strength_patterns = (
        r"\boutperform(?:ed|ing|ance)?\b",
        r"\bresilien(?:t|ce)\b",
        r"\bholding up\b",
        r"\bheld up\b",
        r"\bgaining ground\b",
        r"\bbetter\b",
        r"\bstrong(?:er|est|ly)?\b",
        r"\bbeat\b",
        r"\bahead of\b",
        r"\bpositive relative\b",
        r"\bgrow(?:ing|th)? faster\b",
    )

    weakness = _matches(
        normalized,
        weakness_patterns,
    )

    strength = _matches(
        normalized,
        strength_patterns,
    )

    if weakness > strength:
        return AskIntent.INDUSTRY_WEAKNESS

    if strength > weakness:
        return AskIntent.INDUSTRY_STRENGTH

    return None


def plan_question(
    question: str,
    *,
    explicit_area: str | None = None,
) -> AskPlan:
    normalized = _normalize(question)

    area_fips = _resolve_area(
        question,
        explicit_area,
    )

    #
    # Explicit synthesis requests belong to the guarded
    # language-generation path rather than a deterministic
    # research endpoint.
    #
    interpretive_patterns = (
        r"\bnuanced interpretation\b",
        r"\bcareful interpretation\b",
        r"\bbalanced interpretation\b",
        r"\breasonable interpretation\b",
        r"\banalytical interpretation\b",
        r"\bsynthesi[sz]e\b",
        r"\bsynthesis\b",
        r"\bput .* together\b",
        r"\bconnect .* evidence\b",
        r"\binterpret .* evidence\b",
    )

    if _matches(
        normalized,
        interpretive_patterns,
    ):
        return AskPlan(
            intent=AskIntent.GENERAL_RESEARCH,
            area_fips=area_fips,
            needs_qcew=(area_fips is not None),
            needs_macro=True,
            deterministic_answer=False,
        )

    #
    # High-confidence procedural methodology.
    #
    # These constructions explicitly ask how the research
    # computation works and should not depend on embedding
    # confidence or abstention thresholds.
    #
    procedural_patterns = (
        r"\bhow .* combined\b",
        r"\bhow .* calculated\b",
        r"\bhow .* computed\b",
        r"\bhow .* normalized\b",
        r"\bhow .* smoothed\b",
        r"\bhow .* clustered\b",
        r"\bhow .* detected\b",
        r"\bhow .* validated\b",
    )

    if _matches(
        normalized,
        procedural_patterns,
    ):
        return AskPlan(
            intent=AskIntent.METHODOLOGY,
            area_fips=None,
            needs_qcew=False,
            needs_macro=True,
            deterministic_answer=True,
        )

    #
    # Hard safety boundary.
    #
    # Keep only high-confidence explicit causal language here.
    # Broader causal semantics are handled by the embedding
    # router below.
    #
    hard_causal_patterns = (
        r"\bdid .* cause\b",
        r"\bdoes .* cause\b",
        r"\bwas .* caused by\b",
        r"\bwere .* caused by\b",
        r"\bthe cause of\b",
        r"\bbecause of\b",
        r"\bdue to\b",
        r"\bresponsible for\b",
        r"\battributed to\b",
        r"\bblame .* on\b",
    )

    if _matches(
        normalized,
        hard_causal_patterns,
    ):
        return AskPlan(
            intent=AskIntent.CAUSAL_ATTRIBUTION,
            area_fips=area_fips,
            needs_qcew=(area_fips is not None),
            needs_macro=True,
            deterministic_answer=True,
        )

    #
    # Semantic routing.
    #
    # Lazy import avoids planner <-> semantic_router
    # initialization cycles.
    #
    from laborlens.api.learned_router import (
        learned_route,
    )

    route = learned_route(question)

    #
    # Explicit geography plus industry language is a strong
    # structural signal that the caller expects QCEW-backed
    # industry analysis. The learned classifier may otherwise
    # confuse short phrases such as "which industries were
    # weakening?" with generic macro evidence.
    #
    explicit_industry_query = explicit_area is not None and any(
        token in normalized
        for token in (
            "industry",
            "industries",
            "sector",
            "sectors",
            "employment",
        )
    )

    if explicit_industry_query:
        polarity = _industry_polarity(normalized)

        if polarity is not None:
            return AskPlan(
                intent=polarity,
                area_fips=area_fips,
                needs_qcew=True,
                needs_macro=True,
                deterministic_answer=True,
            )

        return AskPlan(
            intent=AskIntent.INDUSTRY_CONTEXT,
            area_fips=area_fips,
            needs_qcew=True,
            needs_macro=True,
            deterministic_answer=True,
        )

    #
    # Binary causal classification always has priority
    # over ordinary research intent routing.
    #
    if route.intent == AskIntent.CAUSAL_ATTRIBUTION:
        return AskPlan(
            intent=AskIntent.CAUSAL_ATTRIBUTION,
            area_fips=area_fips,
            needs_qcew=(area_fips is not None),
            needs_macro=True,
            deterministic_answer=True,
        )

    intent = route.intent

    #
    # Industry polarity remains deterministic because
    # positive and negative performance language can be
    # extremely close in embedding space.
    #
    industry_intents = {
        AskIntent.INDUSTRY_WEAKNESS,
        AskIntent.INDUSTRY_STRENGTH,
        AskIntent.INDUSTRY_CONTEXT,
    }

    if area_fips is not None and intent in industry_intents:
        polarity = _industry_polarity(normalized)

        if polarity is not None:
            intent = polarity

    deterministic_intents = {
        AskIntent.CAUSAL_ATTRIBUTION,
        AskIntent.EPISODE_SUMMARY,
        AskIntent.MACRO_EVIDENCE,
        AskIntent.INDUSTRY_WEAKNESS,
        AskIntent.INDUSTRY_STRENGTH,
        AskIntent.INDUSTRY_CONTEXT,
        AskIntent.POINT_IN_TIME,
        AskIntent.METHODOLOGY,
    }

    qcew_intents = {
        AskIntent.INDUSTRY_WEAKNESS,
        AskIntent.INDUSTRY_STRENGTH,
        AskIntent.INDUSTRY_CONTEXT,
    }

    geographic_qcew_intents = {
        AskIntent.POINT_IN_TIME,
        AskIntent.GENERAL_RESEARCH,
        AskIntent.CAUSAL_ATTRIBUTION,
    }

    needs_qcew = intent in qcew_intents or (
        intent in geographic_qcew_intents and area_fips is not None
    )

    return AskPlan(
        intent=intent,
        area_fips=area_fips,
        needs_qcew=needs_qcew,
        needs_macro=True,
        deterministic_answer=(intent in deterministic_intents),
    )
