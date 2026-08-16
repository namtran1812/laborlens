import Link from "next/link";

import { EvidenceBars } from "@/components/EvidenceBars";
import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import { getEpisode } from "@/lib/api";

type Props = {
  params: Promise<{
    startDate: string;
  }>;
};

export default async function EpisodePage({
  params,
}: Props) {
  const { startDate } = await params;

  const detail = await getEpisode(startDate);
  const episode = detail.episode;

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <Link
          href="/"
          className="text-sm text-zinc-500 transition hover:text-zinc-200"
        >
          ← Back to LaborLens
        </Link>

        <header className="mt-10 border-b border-zinc-800 pb-10">
          <RegimeBadge type={episode.claim_type} />

          <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight">
            {episode.headline}
          </h1>

          <p className="mt-4 font-mono text-sm text-zinc-500">
            {episode.start_date} → {episode.end_date}
          </p>
        </header>

        <section className="grid gap-4 py-10 md:grid-cols-4">
          <MetricCard
            label="Regime score"
            value={episode.score.toFixed(3)}
          />

          <MetricCard
            label="Confidence"
            value={`${(
              episode.peak_confidence * 100
            ).toFixed(1)}%`}
          />

          <MetricCard
            label="Skeptic"
            value={detail.skeptic.verdict}
            detail={`score ${detail.skeptic.score.toFixed(
              3,
            )}`}
          />

          <MetricCard
            label="Historical percentile"
            value={`${(
              detail.historical_percentile * 100
            ).toFixed(1)}%`}
          />
        </section>

        <section className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
              Supporting evidence
            </div>

            <h2 className="mt-2 text-2xl font-semibold">
              Signal contribution
            </h2>

            <div className="mt-8">
              <EvidenceBars
                signals={
                  detail.evidence.supporting
                }
              />
            </div>
          </div>

          <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
              Research integrity
            </div>

            <div className="mt-6 space-y-6">
              <div>
                <div className="text-sm text-zinc-500">
                  Provenance rows
                </div>
                <div className="mt-1 text-2xl font-semibold">
                  {detail.provenance_rows}
                </div>
              </div>

              <div>
                <div className="text-sm text-zinc-500">
                  Mean episode score
                </div>
                <div className="mt-1 font-mono text-xl">
                  {detail.mean_episode_score.toFixed(
                    3,
                  )}
                </div>
              </div>

              <div>
                <div className="text-sm text-zinc-500">
                  Peak episode score
                </div>
                <div className="mt-1 font-mono text-xl">
                  {detail.peak_episode_score.toFixed(
                    3,
                  )}
                </div>
              </div>

              <div>
                <div className="text-sm text-zinc-500">
                  Opposing signals
                </div>
                <div className="mt-1 text-xl">
                  {detail.evidence.counter.length}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
