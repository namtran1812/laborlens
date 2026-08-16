from __future__ import annotations

from dataclasses import dataclass

import httpx

from laborlens.config import Settings
from laborlens.research.research_bundle import ResearchBundle


@dataclass(frozen=True)
class AssistantAnswer:
    answer: str
    mode: str
    model: str
    sources: tuple[str, ...]
    caveat: str


SUGGESTED_QUESTIONS = (
    "Why was this episode first detected on July 30?",
    "Which indicators contributed most?",
    "How much did later revisions change the conclusion?",
    "What does the 59-day detection latency mean?",
    "Why does LaborLens use point-in-time data?",
)


def demo_answer(
    question: str,
) -> AssistantAnswer:
    normalized = question.lower()

    if "july 30" in normalized or "detected" in normalized:
        answer = (
            "The June 2024 contraction was not detectable through "
            "the July 25 information state. On July 30, new JOLTS "
            "information for JTSHIR and JTSJOL entered the available "
            "information set. With those releases included, the episode "
            "crossed LaborLens's detection criteria with an initial "
            "regime score of -0.446 and confidence of 84.2%."
        )
        sources = (
            "Replay state: 2024-07-25",
            "Replay state: 2024-07-30",
            "Release attribution: JTSHIR, JTSJOL",
        )

    elif "indicator" in normalized or "contribut" in normalized:
        answer = (
            "The strongest standardized supporting contribution was "
            "PAYEMS at -0.85, followed by UNRATE at -0.66, ICSA at "
            "-0.62, and JTSHIR at -0.33. These are standardized "
            "directional contributions, not percentage changes in the "
            "underlying economic series."
        )
        sources = (
            "PAYEMS contribution: -0.850",
            "UNRATE contribution: -0.659",
            "ICSA contribution: -0.622",
            "JTSHIR contribution: -0.326",
        )

    elif "revision" in normalized or "change" in normalized:
        answer = (
            "Later information changed the episode score only modestly. "
            "The initial detected score was -0.446 and the final replay "
            "score was -0.461, an absolute revision of about 0.015. "
            "The episode survived every subsequent replay state, had "
            "no claim-type flips, and its start and end boundaries did "
            "not move."
        )
        sources = (
            "Initial score: -0.4459",
            "Final score: -0.4606",
            "Survival rate: 100%",
            "Claim-type flips: 0",
        )

    elif "59" in normalized or "latency" in normalized:
        answer = (
            "The 59-day detection latency is the difference between "
            "the June 1 episode observation month and the July 30 "
            "information state when enough released data existed for "
            "LaborLens to identify the episode. It is not a 59-day "
            "forecast delay; part of that latency reflects official "
            "economic publication schedules."
        )
        sources = (
            "Episode start: 2024-06-01",
            "First detected as-of: 2024-07-30",
            "Detection latency: 59 days",
        )

    elif "point-in-time" in normalized or "vintage" in normalized:
        answer = (
            "LaborLens uses point-in-time vintages to avoid hindsight "
            "bias. Economic observations can be revised after their "
            "initial release, so evaluating only today's final values "
            "can give a historical model information that did not "
            "actually exist at the time. LaborLens reconstructs the "
            "vintage that was valid at each historical information date."
        )
        sources = (
            "FRED/ALFRED vintage model",
            "realtime_start / realtime_end reconstruction",
        )

    else:
        answer = (
            "For the public demo, LaborLens can answer questions about "
            "the June 2024 contraction, its evidence, detection timing, "
            "release attribution, revision behavior, and point-in-time "
            "methodology. Try one of the suggested research questions."
        )
        sources = ("Validated June 2024 demo research bundle",)

    return AssistantAnswer(
        answer=answer,
        mode="grounded-demo",
        model="validated-research-snapshot",
        sources=sources,
        caveat=(
            "The hosted demo uses validated, deterministic answers. "
            "Live local AI inference is available in research mode."
        ),
    )


def _bundle_context(
    bundle: ResearchBundle,
) -> str:
    support = "\n".join(
        (f"- {item.series_id}: {item.contribution:.3f}") for item in bundle.evidence.supporting
    )

    opposing = "\n".join(
        (f"- {item.series_id}: {item.contribution:.3f}") for item in bundle.evidence.opposing
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

Supporting evidence:
{support or "none"}

Opposing evidence:
{opposing or "none"}

Historical percentile:
{bundle.historical_percentile:.3f}

Rules:
- Do not invent causes.
- Do not invent statistics.
- Distinguish standardized contributions from natural-unit changes.
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

Answer only from the verified research context below.
If the context does not establish something, say so explicitly.

VERIFIED CONTEXT
----------------
{_bundle_context(bundle)}

USER QUESTION
-------------
{question}

Write a concise research answer.
Do not introduce any unsupported dates, values, causal claims,
or external facts.
""".strip()

    response = httpx.post(
        f"{settings.ollama_host.rstrip('/')}/api/generate",
        json={
            "model": settings.laborlens_model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.1,
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

    return AssistantAnswer(
        answer=answer,
        mode="local-ai",
        model=settings.laborlens_model,
        sources=tuple(item.series_id for item in bundle.evidence.supporting),
        caveat=("AI explanation generated from a verified LaborLens research bundle."),
    )
