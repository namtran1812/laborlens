const API_BASE =
  process.env.NEXT_PUBLIC_LABORLENS_API_URL ??
  "http://localhost:8000";

export type Episode = {
  episode_id: string;
  claim_type: string;
  start_date: string;
  end_date: string;
  duration_months: number;
  peak_confidence: number;
  score: number;
  headline: string;
};

export type EpisodeListResponse = {
  count: number;
  episodes: Episode[];
};

export type EvidenceSignal = {
  series_id: string;
  contribution: number;
};

export type EpisodeDetail = {
  episode: Episode;
  skeptic: {
    verdict: string;
    score: number;
  };
  evidence: {
    supporting: EvidenceSignal[];
    counter: EvidenceSignal[];
  };
  historical_percentile: number;
  mean_episode_score: number;
  peak_episode_score: number;
  provenance_rows: number;
};

export async function getEpisodes(): Promise<EpisodeListResponse> {
  const response = await fetch(
    `${API_BASE}/episodes?window=24&min_confidence=0.55`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to load episodes");
  }

  return response.json();
}

export async function getEpisode(
  startDate: string,
  asOf?: string,
): Promise<EpisodeDetail> {
  const params = new URLSearchParams();

  if (asOf) {
    params.set("as_of", asOf);
  }

  const query = params.toString();
  const url =
    `${API_BASE}/episodes/${startDate}` +
    (query ? `?${query}` : "");

  const response = await fetch(url, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load episode");
  }

  return response.json();
}

export type ReplayEpisode = {
  episode_id: string;
  claim_type: string;
  start_date: string;
  end_date: string;
  score: number;
  confidence: number;
};

export type ReplayState = {
  as_of_date: string;
  detected: boolean;
  episode: ReplayEpisode | null;
};

export type ReplayMetrics = {
  replay_dates: number;
  detected_states: number;
  missing_states: number;
  first_detected_as_of: string | null;
  previous_information_state: string | null;
  last_detected_as_of: string | null;
  detection_release_series: string[];
  detection_latency_days: number | null;
  survival_rate: number | null;
  claim_type_flips: number;
  initial_score: number | null;
  final_score: number | null;
  absolute_score_revision: number | null;
  initial_confidence: number | null;
  final_confidence: number | null;
  mean_score_drift: number | null;
  max_score_drift: number | null;
  start_drift_months: number | null;
  end_drift_months: number | null;
};

export type ReplayResponse = {
  target: string;
  schedule: string;
  from_date: string;
  to_date: string;
  reference_episode:
    | (ReplayEpisode & {
        headline: string;
      })
    | null;
  states: ReplayState[];
  metrics: ReplayMetrics;
};

export async function getReplay(options: {
  from: string;
  to: string;
  target: string;
  schedule?: "releases" | "fixed";
  window?: number;
  minConfidence?: number;
}): Promise<ReplayResponse> {
  const params = new URLSearchParams({
    from: options.from,
    to: options.to,
    target: options.target,
    schedule: options.schedule ?? "releases",
    window: String(options.window ?? 24),
    min_confidence: String(
      options.minConfidence ?? 0.55,
    ),
  });

  const response = await fetch(
    `${API_BASE}/replay?${params.toString()}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load historical replay",
    );
  }

  return response.json();
}
