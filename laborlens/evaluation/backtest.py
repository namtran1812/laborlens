from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import fmean, median

from laborlens.analysis.regime import DEFAULT_SPECS
from laborlens.evaluation.replay import (
    ReplayEvaluation,
    evaluate_replay,
)
from laborlens.research.episodes import (
    ClaimEpisode,
)
from laborlens.services.research_pipeline import (
    ResearchPipeline,
)
from laborlens.storage.clickhouse import (
    ClickHouseStore,
)


@dataclass(frozen=True)
class EpisodeBacktest:
    target_date: date
    claim_type: str

    final_start_date: date
    final_end_date: date

    replay: ReplayEvaluation


@dataclass(frozen=True)
class EpisodeFamily:
    family_id: int

    first_seen_as_of: date
    last_seen_as_of: date

    first_episode: ClaimEpisode
    final_episode: ClaimEpisode

    observations: int

    persistent_to_final: bool
    type_flipped: bool

    start_drift_months: int
    end_drift_months: int


@dataclass(frozen=True)
class BacktestSummary:
    episodes: tuple[EpisodeBacktest, ...]
    families: tuple[EpisodeFamily, ...]

    # Final-state reference evaluation.
    episodes_evaluated: int
    episodes_detected: int
    episodes_never_detected: int

    detection_rate: float | None

    median_detection_latency_days: float | None
    p90_detection_latency_days: float | None

    mean_survival_rate: float | None
    median_survival_rate: float | None

    claim_type_flip_rate: float | None

    mean_absolute_score_revision: float | None
    median_absolute_score_revision: float | None
    p90_absolute_score_revision: float | None

    mean_start_drift_months: float | None
    mean_end_drift_months: float | None

    # Anti-survivorship evaluation.
    realtime_episode_families: int
    persistent_families: int
    disappeared_families: int
    final_only_families: int

    persistence_rate: float | None
    revision_disappearance_rate: float | None

    type_flipped_families: int
    type_flip_family_rate: float | None

    mean_family_start_drift_months: float | None
    mean_family_end_drift_months: float | None


def _percentile(
    values: list[float],
    percentile: float,
) -> float | None:
    if not values:
        return None

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = percentile * (len(ordered) - 1)

    lower = int(position)

    upper = min(
        lower + 1,
        len(ordered) - 1,
    )

    weight = position - lower

    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _month_index(
    value: date,
) -> int:
    return value.year * 12 + value.month


def _month_distance(
    left: date,
    right: date,
) -> int:
    return _month_index(right) - _month_index(left)


def _overlap_months(
    left: ClaimEpisode,
    right: ClaimEpisode,
) -> int:
    start = max(
        _month_index(left.start_date),
        _month_index(right.start_date),
    )

    end = min(
        _month_index(left.end_date),
        _month_index(right.end_date),
    )

    if start > end:
        return 0

    return end - start + 1


def _family_match_score(
    previous: ClaimEpisode,
    current: ClaimEpisode,
) -> tuple[int, int, int] | None:
    overlap = _overlap_months(
        previous,
        current,
    )

    if overlap == 0:
        return None

    same_type = int(previous.claim_type == current.claim_type)

    representative_distance = abs(
        _month_distance(
            previous.representative.observation_date,
            current.representative.observation_date,
        )
    )

    return (
        overlap,
        same_type,
        -representative_distance,
    )


def _build_episode_families(
    states: list[
        tuple[
            date,
            list[ClaimEpisode],
        ]
    ],
    *,
    start_date: date,
    end_date: date,
) -> list[EpisodeFamily]:
    mutable: list[
        list[
            tuple[
                date,
                ClaimEpisode,
            ]
        ]
    ] = []

    for (
        as_of_date,
        episodes,
    ) in states:
        eligible = [
            episode for episode in episodes if (start_date <= episode.start_date <= end_date)
        ]

        used_families: set[int] = set()

        for episode in eligible:
            best_family = None
            best_score = None

            for (
                index,
                observations,
            ) in enumerate(mutable):
                if index in used_families:
                    continue

                previous = observations[-1][1]

                score = _family_match_score(
                    previous,
                    episode,
                )

                if score is None:
                    continue

                if best_score is None or score > best_score:
                    best_family = index
                    best_score = score

            if best_family is None:
                mutable.append(
                    [
                        (
                            as_of_date,
                            episode,
                        )
                    ]
                )

                used_families.add(len(mutable) - 1)

            else:
                mutable[best_family].append(
                    (
                        as_of_date,
                        episode,
                    )
                )

                used_families.add(best_family)

    result = []

    for (
        family_id,
        observations,
    ) in enumerate(
        mutable,
        start=1,
    ):
        first_seen, first_episode = observations[0]

        last_seen, final_episode = observations[-1]

        claim_types = {episode.claim_type for _, episode in observations}

        result.append(
            EpisodeFamily(
                family_id=family_id,
                first_seen_as_of=(first_seen),
                last_seen_as_of=(last_seen),
                first_episode=(first_episode),
                final_episode=(final_episode),
                observations=len(observations),
                persistent_to_final=(last_seen == end_date),
                type_flipped=(len(claim_types) > 1),
                start_drift_months=(
                    _month_distance(
                        first_episode.start_date,
                        final_episode.start_date,
                    )
                ),
                end_drift_months=(
                    _month_distance(
                        first_episode.end_date,
                        final_episode.end_date,
                    )
                ),
            )
        )

    return result


def run_backtest(
    store: ClickHouseStore,
    pipeline: ResearchPipeline,
    *,
    start_date: date,
    end_date: date,
    window: int = 24,
    min_confidence: float = 0.55,
) -> BacktestSummary:
    information_dates = store.information_dates(
        list(DEFAULT_SPECS.keys()),
        start_date,
        end_date,
    )

    if not information_dates:
        raise ValueError("no information dates found in requested backtest range")

    if information_dates[-1] != end_date:
        information_dates.append(end_date)

    # -----------------------------------------------------
    # 1. Discover every real-time state once.
    # -----------------------------------------------------

    historical_states = []

    for as_of_date in information_dates:
        episodes = pipeline.discover_episodes(
            window=window,
            min_confidence=min_confidence,
            as_of_date=as_of_date,
        )

        historical_states.append(
            (
                as_of_date,
                episodes,
            )
        )

    families = _build_episode_families(
        historical_states,
        start_date=start_date,
        end_date=end_date,
    )

    # -----------------------------------------------------
    # 2. Final-state episode evaluation.
    # -----------------------------------------------------

    final_episodes = pipeline.discover_episodes(
        window=window,
        min_confidence=min_confidence,
        as_of_date=end_date,
    )

    reference_episodes = [
        episode for episode in final_episodes if (start_date <= episode.start_date <= end_date)
    ]

    results = []

    for episode in reference_episodes:
        replay = evaluate_replay(
            pipeline,
            start_date=start_date,
            end_date=end_date,
            target_date=(episode.start_date),
            window=window,
            min_confidence=(min_confidence),
            evaluation_dates=(information_dates),
        )

        results.append(
            EpisodeBacktest(
                target_date=(episode.start_date),
                claim_type=(episode.claim_type),
                final_start_date=(episode.start_date),
                final_end_date=(episode.end_date),
                replay=replay,
            )
        )

    detected = [item for item in results if (item.replay.first_detected_as_of is not None)]

    latencies = [
        float(item.replay.detection_latency_days)
        for item in detected
        if (item.replay.detection_latency_days is not None)
    ]

    survival_rates = [
        item.replay.survival_rate for item in detected if (item.replay.survival_rate is not None)
    ]

    score_revisions = [
        item.replay.absolute_score_revision
        for item in detected
        if (item.replay.absolute_score_revision is not None)
    ]

    start_drifts = [
        float(item.replay.start_drift_months)
        for item in detected
        if (item.replay.start_drift_months is not None)
    ]

    end_drifts = [
        float(item.replay.end_drift_months)
        for item in detected
        if (item.replay.end_drift_months is not None)
    ]

    episodes_evaluated = len(results)

    episodes_detected = len(detected)

    type_flip_count = sum(item.replay.claim_type_flips > 0 for item in detected)

    # -----------------------------------------------------
    # 3. Anti-survivorship metrics.
    # -----------------------------------------------------

    persistent = [family for family in families if family.persistent_to_final]

    disappeared = [family for family in families if not family.persistent_to_final]

    final_only = [family for family in families if (family.first_seen_as_of == end_date)]

    flipped = [family for family in families if family.type_flipped]

    family_start_drifts = [float(family.start_drift_months) for family in families]

    family_end_drifts = [float(family.end_drift_months) for family in families]

    family_count = len(families)

    return BacktestSummary(
        episodes=tuple(results),
        families=tuple(families),
        episodes_evaluated=(episodes_evaluated),
        episodes_detected=(episodes_detected),
        episodes_never_detected=(episodes_evaluated - episodes_detected),
        detection_rate=(episodes_detected / episodes_evaluated if episodes_evaluated else None),
        median_detection_latency_days=(median(latencies) if latencies else None),
        p90_detection_latency_days=(
            _percentile(
                latencies,
                0.90,
            )
        ),
        mean_survival_rate=(fmean(survival_rates) if survival_rates else None),
        median_survival_rate=(median(survival_rates) if survival_rates else None),
        claim_type_flip_rate=(type_flip_count / episodes_detected if episodes_detected else None),
        mean_absolute_score_revision=(fmean(score_revisions) if score_revisions else None),
        median_absolute_score_revision=(median(score_revisions) if score_revisions else None),
        p90_absolute_score_revision=(
            _percentile(
                score_revisions,
                0.90,
            )
        ),
        mean_start_drift_months=(fmean(start_drifts) if start_drifts else None),
        mean_end_drift_months=(fmean(end_drifts) if end_drifts else None),
        realtime_episode_families=(family_count),
        persistent_families=len(persistent),
        disappeared_families=len(disappeared),
        final_only_families=len(final_only),
        persistence_rate=(len(persistent) / family_count if family_count else None),
        revision_disappearance_rate=(len(disappeared) / family_count if family_count else None),
        type_flipped_families=len(flipped),
        type_flip_family_rate=(len(flipped) / family_count if family_count else None),
        mean_family_start_drift_months=(
            fmean(family_start_drifts) if family_start_drifts else None
        ),
        mean_family_end_drift_months=(fmean(family_end_drifts) if family_end_drifts else None),
    )
