from __future__ import annotations

from datetime import date

DEMO_EPISODE = {
    "episode_id": ("broad_contraction-2024-06-01-2024-06-01"),
    "claim_type": "broad_contraction",
    "start_date": "2024-06-01",
    "end_date": "2024-06-01",
    "duration_months": 1,
    "peak_confidence": 0.8430936516010492,
    "score": -0.4606394461100772,
    "headline": ("Labor-market indicators are weakening broadly"),
}


DEMO_DETAIL = {
    "episode": DEMO_EPISODE,
    "skeptic": {
        "verdict": "supported",
        "score": 0.8374192960869964,
    },
    "evidence": {
        "supporting": [
            {
                "series_id": "PAYEMS",
                "contribution": (-0.8504794920126176),
            },
            {
                "series_id": "UNRATE",
                "contribution": (-0.6586724681757263),
            },
            {
                "series_id": "ICSA",
                "contribution": (-0.6222862334192558),
            },
            {
                "series_id": "JTSHIR",
                "contribution": (-0.325821396606375),
            },
        ],
        "counter": [],
    },
    "historical_percentile": (0.6666666666666666),
    "mean_episode_score": (-0.4606394461100772),
    "peak_episode_score": (-0.4606394461100772),
    "provenance_rows": 5,
}


DEMO_ARTICLE = """# Labor-market indicators are weakening broadly

## Direct answer

LaborLens identified a broad contraction episode from 2024-06-01 through 2024-06-01. The deterministic skeptic classified the episode as **supported**.

## What changed?

The episode lasted 1 month(s). Its mean smoothed regime score was -0.461, with a peak episode score of -0.461.

## Evidence

- **Total nonfarm payroll employment (PAYEMS)**: standardized contribution -0.85
- **Unemployment rate (UNRATE)**: standardized contribution -0.66
- **Initial unemployment claims (ICSA)**: standardized contribution -0.62
- **Hires rate (JTSHIR)**: standardized contribution -0.33

No material opposing signal was identified by the deterministic evidence filter.

## Historical context

The episode ranked at the 66.7th percentile among 42 comparable regime observations spanning 2021-01-01 through 2024-06-01.

The closest same-type historical comparison was:

- 2022-05-01 through 2023-08-01: score -0.788

## What this does not establish

The analysis identifies statistical co-movement across labor-market indicators. It does not by itself establish causation, identify a policy or economic mechanism, or prove that historical comparisons had the same underlying causes.

## Methodology

LaborLens normalizes each indicator against its rolling history, aligns directional signals, smooths the composite regime, clusters adjacent claims into episodes, and subjects each episode to deterministic evidence and skeptic checks before writing.
"""


_DEMO_DATES = [
    "2024-06-04",
    "2024-06-06",
    "2024-06-07",
    "2024-06-13",
    "2024-06-20",
    "2024-06-27",
    "2024-07-02",
    "2024-07-03",
    "2024-07-05",
    "2024-07-11",
    "2024-07-18",
    "2024-07-25",
    "2024-07-30",
    "2024-08-01",
    "2024-08-02",
    "2024-08-08",
    "2024-08-15",
    "2024-08-22",
    "2024-08-29",
    "2024-09-01",
]


def _replay_episode(
    *,
    score: float,
    confidence: float,
) -> dict:
    return {
        "episode_id": (DEMO_EPISODE["episode_id"]),
        "claim_type": (DEMO_EPISODE["claim_type"]),
        "start_date": "2024-06-01",
        "end_date": "2024-06-01",
        "score": score,
        "confidence": confidence,
    }


def _demo_states() -> list[dict]:
    states = []

    for value in _DEMO_DATES:
        if value < "2024-07-30":
            episode = None

        elif value < "2024-08-02":
            episode = _replay_episode(
                score=-0.4458961487641862,
                confidence=(0.8423167204911545),
            )

        else:
            episode = _replay_episode(
                score=-0.4606394461100772,
                confidence=(0.8430936516010492),
            )

        states.append(
            {
                "as_of_date": value,
                "detected": (episode is not None),
                "episode": episode,
            }
        )

    return states


DEMO_REPLAY = {
    "target": "2024-06-01",
    "schedule": "releases",
    "from_date": "2024-06-01",
    "to_date": "2024-09-01",
    "reference_episode": {
        "episode_id": (DEMO_EPISODE["episode_id"]),
        "claim_type": (DEMO_EPISODE["claim_type"]),
        "start_date": "2024-06-01",
        "end_date": "2024-06-01",
        "headline": (DEMO_EPISODE["headline"]),
        "score": -0.4606394461100772,
        "confidence": 0.8430936516010492,
    },
    "states": _demo_states(),
    "metrics": {
        "replay_dates": 20,
        "detected_states": 8,
        "missing_states": 12,
        "first_detected_as_of": ("2024-07-30"),
        "previous_information_state": ("2024-07-25"),
        "last_detected_as_of": ("2024-09-01"),
        "detection_release_series": [
            "JTSHIR",
            "JTSJOL",
        ],
        "detection_latency_days": 59,
        "survival_rate": 1.0,
        "claim_type_flips": 0,
        "initial_score": (-0.4458961487641862),
        "final_score": (-0.4606394461100772),
        "absolute_score_revision": (0.014743297345890971),
        "initial_confidence": (0.8423167204911545),
        "final_confidence": (0.8430936516010492),
        "mean_score_drift": (0.0021061853351272814),
        "max_score_drift": (0.014743297345890971),
        "start_drift_months": 0,
        "end_drift_months": 0,
    },
}


def demo_episodes() -> dict:
    return {
        "count": 1,
        "episodes": [
            DEMO_EPISODE,
        ],
    }


def demo_episode_detail(
    start_date: date,
) -> dict | None:
    if start_date != date(
        2024,
        6,
        1,
    ):
        return None

    return DEMO_DETAIL


def demo_article(
    start_date: date,
) -> dict | None:
    if start_date != date(
        2024,
        6,
        1,
    ):
        return None

    return {
        "episode_id": (DEMO_EPISODE["episode_id"]),
        "article": DEMO_ARTICLE,
    }


def demo_replay(
    *,
    target: date,
) -> dict | None:
    if target != date(
        2024,
        6,
        1,
    ):
        return None

    return DEMO_REPLAY
