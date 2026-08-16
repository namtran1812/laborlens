from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import fmean

from laborlens.research.episodes import ClaimEpisode
from laborlens.services.research_pipeline import ResearchPipeline


@dataclass(frozen=True)
class ReplayState:
    as_of_date: date
    episodes: tuple[ClaimEpisode, ...]


@dataclass(frozen=True)
class TrackedState:
    as_of_date: date
    episode: ClaimEpisode | None


@dataclass(frozen=True)
class ReplayEvaluation:
    states: tuple[ReplayState, ...]
    tracked: tuple[TrackedState, ...]

    reference_episode: ClaimEpisode | None

    replay_dates: int
    detected_states: int
    missing_states: int

    first_detected_as_of: date | None
    previous_information_state: date | None
    last_detected_as_of: date | None
    detection_latency_days: int | None

    survival_rate: float | None
    claim_type_flips: int

    initial_score: float | None
    final_score: float | None
    absolute_score_revision: float | None

    initial_confidence: float | None
    final_confidence: float | None

    mean_score_drift: float | None
    max_score_drift: float | None

    start_drift_months: int | None
    end_drift_months: int | None


def replay_dates(
    start_date: date,
    end_date: date,
    *,
    step_days: int,
) -> list[date]:
    if step_days < 1:
        raise ValueError("step_days must be positive")

    if start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")

    result = []
    current = start_date

    while current <= end_date:
        result.append(current)
        current += timedelta(days=step_days)

    if result[-1] != end_date:
        result.append(end_date)

    return result


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


def _match_episode(
    reference: ClaimEpisode,
    candidates: tuple[ClaimEpisode, ...],
) -> ClaimEpisode | None:
    overlapping = [
        episode
        for episode in candidates
        if _overlap_months(
            reference,
            episode,
        )
        > 0
    ]

    if not overlapping:
        return None

    return max(
        overlapping,
        key=lambda episode: (
            _overlap_months(
                reference,
                episode,
            ),
            int(episode.claim_type == reference.claim_type),
            episode.peak_confidence,
            -abs(
                _month_distance(
                    reference.representative.observation_date,
                    episode.representative.observation_date,
                )
            ),
        ),
    )


def _reference_episode(
    state: ReplayState,
    target_date: date,
) -> ClaimEpisode | None:
    candidates = [
        episode
        for episode in state.episodes
        if (episode.start_date <= target_date <= episode.end_date)
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda episode: (
            episode.peak_confidence,
            abs(episode.representative.score),
        ),
    )


def evaluate_replay(
    pipeline: ResearchPipeline,
    *,
    start_date: date,
    end_date: date,
    target_date: date,
    step_days: int = 30,
    window: int = 24,
    min_confidence: float = 0.55,
    evaluation_dates: list[date] | None = None,
) -> ReplayEvaluation:
    if evaluation_dates is None:
        dates = replay_dates(
            start_date,
            end_date,
            step_days=step_days,
        )
    else:
        dates = sorted({value for value in evaluation_dates if (start_date <= value <= end_date)})

        if not dates:
            raise ValueError("evaluation_dates contains no dates in the requested range")

        if dates[-1] != end_date:
            dates.append(end_date)

    states = []

    for as_of_date in dates:
        episodes = pipeline.discover_episodes(
            window=window,
            min_confidence=min_confidence,
            as_of_date=as_of_date,
        )

        states.append(
            ReplayState(
                as_of_date=as_of_date,
                episodes=tuple(episodes),
            )
        )

    reference = _reference_episode(
        states[-1],
        target_date,
    )

    tracked = []

    for state in states:
        episode = (
            _match_episode(
                reference,
                state.episodes,
            )
            if reference is not None
            else None
        )

        tracked.append(
            TrackedState(
                as_of_date=state.as_of_date,
                episode=episode,
            )
        )

    detected = [state for state in tracked if state.episode is not None]

    if not detected:
        return ReplayEvaluation(
            states=tuple(states),
            tracked=tuple(tracked),
            reference_episode=reference,
            replay_dates=len(states),
            detected_states=0,
            missing_states=len(states),
            first_detected_as_of=None,
            previous_information_state=None,
            last_detected_as_of=None,
            detection_latency_days=None,
            survival_rate=None,
            claim_type_flips=0,
            initial_score=None,
            final_score=None,
            absolute_score_revision=None,
            initial_confidence=None,
            final_confidence=None,
            mean_score_drift=None,
            max_score_drift=None,
            start_drift_months=None,
            end_drift_months=None,
        )

    first = detected[0]
    last = detected[-1]

    first_index = next(
        index for index, state in enumerate(tracked) if state.as_of_date == first.as_of_date
    )

    previous_information_state = tracked[first_index - 1].as_of_date if first_index > 0 else None

    first_episode = first.episode
    last_episode = last.episode

    assert first_episode is not None
    assert last_episode is not None

    eligible = [state for state in tracked if state.as_of_date >= first.as_of_date]

    survival_rate = sum(state.episode is not None for state in eligible) / len(eligible)

    claim_type_flips = 0
    drifts = []
    previous_episode = None

    for state in tracked:
        current = state.episode

        if current is None:
            continue

        if previous_episode is not None:
            if previous_episode.claim_type != current.claim_type:
                claim_type_flips += 1

            drifts.append(abs(current.representative.score - previous_episode.representative.score))

        previous_episode = current

    initial_score = first_episode.representative.score

    final_score = last_episode.representative.score

    initial_confidence = first_episode.peak_confidence

    final_confidence = last_episode.peak_confidence

    return ReplayEvaluation(
        states=tuple(states),
        tracked=tuple(tracked),
        reference_episode=reference,
        replay_dates=len(states),
        detected_states=len(detected),
        missing_states=(len(states) - len(detected)),
        first_detected_as_of=(first.as_of_date),
        previous_information_state=(previous_information_state),
        last_detected_as_of=(last.as_of_date),
        detection_latency_days=(first.as_of_date - reference.start_date).days
        if reference is not None
        else None,
        survival_rate=survival_rate,
        claim_type_flips=claim_type_flips,
        initial_score=initial_score,
        final_score=final_score,
        absolute_score_revision=abs(final_score - initial_score),
        initial_confidence=initial_confidence,
        final_confidence=final_confidence,
        mean_score_drift=(fmean(drifts) if drifts else 0.0),
        max_score_drift=(max(drifts) if drifts else 0.0),
        start_drift_months=(
            _month_distance(
                first_episode.start_date,
                last_episode.start_date,
            )
        ),
        end_drift_months=(
            _month_distance(
                first_episode.end_date,
                last_episode.end_date,
            )
        ),
    )
