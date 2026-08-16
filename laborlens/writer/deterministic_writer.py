from __future__ import annotations

from laborlens.research.research_bundle import ResearchBundle
from laborlens.research.series_catalog import series_name


def _signal_sentence(
    series_id: str,
    contribution: float,
) -> str:
    name = series_name(series_id)

    return f"- **{name} ({series_id})**: standardized contribution {contribution:.2f}"


def write_deterministic_article(
    bundle: ResearchBundle,
) -> str:
    episode = bundle.episode

    lines = [
        f"# {bundle.claim.headline}",
        "",
        "## Direct answer",
        "",
        (
            f"LaborLens identified a "
            f"{bundle.claim.claim_type.replace('_', ' ')} "
            f"episode from {episode.start_date} "
            f"through {episode.end_date}. "
            f"The deterministic skeptic classified the "
            f"episode as **{bundle.skeptic.verdict}**."
        ),
        "",
        "## What changed?",
        "",
        (
            f"The episode lasted {bundle.duration_months} "
            f"month(s). Its mean smoothed regime score was "
            f"{bundle.mean_episode_score:.3f}, with a peak "
            f"episode score of {bundle.peak_episode_score:.3f}."
        ),
        "",
        "## Evidence",
        "",
    ]

    for item in bundle.evidence.supporting:
        lines.append(
            _signal_sentence(
                item.series_id,
                item.contribution,
            )
        )

    if bundle.evidence.opposing:
        lines.extend(
            [
                "",
                "Counter-signals:",
                "",
            ]
        )

        for item in bundle.evidence.opposing:
            lines.append(
                _signal_sentence(
                    item.series_id,
                    item.contribution,
                )
            )
    else:
        lines.extend(
            [
                "",
                (
                    "No material opposing signal was identified "
                    "by the deterministic evidence filter."
                ),
            ]
        )

    lines.extend(
        [
            "",
            "## Historical context",
            "",
            (
                f"The episode ranked at the "
                f"{bundle.historical_percentile:.1%} "
                f"historical percentile within the comparable "
                f"observations evaluated by LaborLens."
            ),
            "",
        ]
    )

    if bundle.historical_analogs:
        lines.append("The closest same-type historical comparisons were:")
        lines.append("")

        for analog in bundle.historical_analogs:
            lines.append(
                f"- {analog.start_date} through {analog.end_date}: score {analog.score:.3f}"
            )
    else:
        lines.append("No same-type historical analog was available.")

    lines.extend(
        [
            "",
            "## What this does not establish",
            "",
            (
                "The analysis identifies statistical co-movement "
                "across labor-market indicators. It does not by "
                "itself establish causation, identify a policy or "
                "economic mechanism, or prove that historical "
                "comparisons had the same underlying causes."
            ),
            "",
            "## Methodology",
            "",
            (
                "LaborLens normalizes each indicator against its "
                "rolling history, aligns directional signals, "
                "smooths the composite regime, clusters adjacent "
                "claims into episodes, and subjects each episode "
                "to deterministic evidence and skeptic checks "
                "before writing."
            ),
        ]
    )

    return "\n".join(lines)
