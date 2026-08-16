import Link from "next/link";

import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import { getEpisodes } from "@/lib/api";

export default async function Home() {
  const data = await getEpisodes();
  const latest = data.episodes.at(-1);

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <header className="flex flex-col gap-6 border-b border-zinc-800 pb-10 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-sm uppercase tracking-[0.25em] text-zinc-500">
              LaborLens
            </div>

            <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
              Point-in-time labor-market intelligence.
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-7 text-zinc-400">
              Revision-aware economic research built from
              FRED/ALFRED vintages, regime detection,
              evidence scoring, and historical replay.
            </p>
          </div>

          <div className="flex gap-3">
            <Link
              href="/replay"
              className="rounded-full border border-zinc-700 px-4 py-2 text-xs uppercase tracking-[0.18em] text-zinc-300 transition hover:bg-zinc-900"
            >
              Replay explorer
            </Link>

            <div className="rounded-full border border-zinc-800 px-4 py-2 text-xs uppercase tracking-[0.18em] text-zinc-500">
              Research mode
            </div>
          </div>
        </header>

        {latest ? (
          <>
            <section className="grid gap-4 py-10 md:grid-cols-4">
              <MetricCard
                label="Current regime"
                value={latest.claim_type.replaceAll(
                  "_",
                  " ",
                )}
              />

              <MetricCard
                label="Score"
                value={latest.score.toFixed(3)}
              />

              <MetricCard
                label="Confidence"
                value={`${(
                  latest.peak_confidence * 100
                ).toFixed(1)}%`}
              />

              <MetricCard
                label="Episode"
                value={latest.start_date}
              />
            </section>

            <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
              <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
                <div>
                  <RegimeBadge
                    type={latest.claim_type}
                  />

                  <h2 className="mt-5 text-2xl font-semibold">
                    {latest.headline}
                  </h2>

                  <p className="mt-3 max-w-2xl text-zinc-400">
                    Latest detected episode from the
                    current information set.
                  </p>
                </div>

                <Link
                  href={`/episodes/${latest.start_date}`}
                  className="inline-flex rounded-xl border border-zinc-700 px-4 py-2 text-sm text-zinc-200 transition hover:bg-zinc-900"
                >
                  Open research view
                </Link>
              </div>
            </section>
          </>
        ) : (
          <section className="py-12 text-zinc-400">
            No episodes detected.
          </section>
        )}

        <section className="py-12">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                Historical regimes
              </div>
              <h2 className="mt-2 text-2xl font-semibold">
                Detected episodes
              </h2>
            </div>

            <div className="text-sm text-zinc-500">
              {data.count} total
            </div>
          </div>

          <div className="space-y-3">
            {data.episodes.map((episode) => (
              <Link
                key={episode.episode_id}
                href={`/episodes/${episode.start_date}`}
                className="grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5 transition hover:border-zinc-600 md:grid-cols-[180px_1fr_150px]"
              >
                <div className="font-mono text-sm text-zinc-400">
                  {episode.start_date}
                </div>

                <div>
                  <div className="font-medium text-zinc-100">
                    {episode.headline}
                  </div>

                  <div className="mt-2">
                    <RegimeBadge
                      type={episode.claim_type}
                    />
                  </div>
                </div>

                <div className="text-right font-mono text-sm text-zinc-400">
                  {episode.score.toFixed(3)}
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
