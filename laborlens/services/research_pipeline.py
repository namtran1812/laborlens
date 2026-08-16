from __future__ import annotations

from datetime import date

from laborlens.analysis.regime import (
    DEFAULT_SPECS,
    compute_regime,
    compute_signal,
)
from laborlens.research.claims import (
    discover_claims,
)
from laborlens.research.episodes import (
    cluster_claims,
)
from laborlens.research.evidence import (
    build_evidence_bundle,
)
from laborlens.research.research_bundle import (
    ProvenanceItem,
    ResearchBundle,
    build_research_bundle,
)
from laborlens.research.skeptic import (
    review_evidence,
)
from laborlens.storage.clickhouse import (
    ClickHouseStore,
)


class ResearchPipeline:
    def __init__(
        self,
        store: ClickHouseStore,
    ) -> None:
        self.store = store

    def build(
        self,
        *,
        start_date: date,
        window: int = 24,
        min_confidence: float = 0.55,
    ) -> ResearchBundle:
        signals = {}

        for (
            series_id,
            spec,
        ) in DEFAULT_SPECS.items():
            rows = self.store.latest_snapshot(series_id)

            if not rows:
                continue

            points = [
                (
                    row[0],
                    float(row[1]),
                )
                for row in rows
                if row[1] is not None
            ]

            signals[series_id] = compute_signal(
                points,
                spec,
                window=window,
            )

        regimes = compute_regime(signals)

        claims = discover_claims(
            regimes,
            min_confidence=(min_confidence),
        )

        episodes = cluster_claims(claims)

        matches = [episode for episode in episodes if (episode.start_date == start_date)]

        if not matches:
            raise ValueError(f"no research episode starts on {start_date}")

        episode = matches[0]

        evidence = build_evidence_bundle(episode)

        skeptic = review_evidence(evidence)

        provenance = []

        for series_id in DEFAULT_SPECS:
            rows = self.store.provenance_for_window(
                series_id,
                episode.start_date,
                episode.end_date,
            )

            for row in rows:
                if row[1] is None:
                    continue

                provenance.append(
                    ProvenanceItem(
                        series_id=series_id,
                        observation_date=(row[0]),
                        value=float(row[1]),
                        realtime_start=(row[2]),
                        realtime_end=(row[3]),
                    )
                )

        return build_research_bundle(
            episode=episode,
            evidence=evidence,
            skeptic=skeptic,
            regimes=regimes,
            all_episodes=episodes,
            provenance=provenance,
        )
