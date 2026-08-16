import Link from "next/link";

import { AppNav } from "@/components/AppNav";
import { DemoNotice } from "@/components/DemoNotice";
import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import {
  getEpisodes,
  getMeta,
} from "@/lib/api";

export default async function Home() {
  const [data, meta] =
    await Promise.all([
      getEpisodes(),
      getMeta(),
    ]);

  const latest =
    data.episodes.at(-1);

  return (
    <main className="min-h-screen bg-black text-white">
      <AppNav mode={meta.mode} />

      <div className="mx-auto max-w-6xl px-6 py-12">
        <DemoNotice
          mode={meta.mode}
        />

        <header className="mt-10 border-b border-zinc-800 pb-12">
          <div className="text-xs uppercase tracking-[0.25em] text-zinc-500">
            Revision-aware economic research
          </div>

          <h1 className="mt-5 max-w-4xl text-5xl font-semibold tracking-tight md:text-7xl">
            What did the labor market
            look like with only the
            information available then?
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-zinc-400">
            LaborLens reconstructs historical
            FRED/ALFRED information states,
            detects labor-market regimes,
            measures revision stability, and
            explains validated findings through
            a grounded research assistant.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/replay?target=2024-06-01&from=2024-06-01&to=2024-09-01"
              className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
            >
              Explore June 2024 replay
            </Link>

            {latest ? (
              <Link
                href={`/episodes/${latest.start_date}`}
                className="rounded-xl border border-zinc-700 px-5 py-3 text-sm text-zinc-200 transition hover:bg-zinc-900"
              >
                Open research workspace
              </Link>
            ) : null}
          </div>
        </header>

        {latest ? (
          <>
            <section className="grid gap-4 py-10 md:grid-cols-4">
              <MetricCard
                label="Regime"
                value={latest.claim_type.replaceAll(
                  "_",
                  " ",
                )}
              />

              <MetricCard
                label="Score"
                value={latest.score.toFixed(
                  3,
                )}
              />

              <MetricCard
                label="Confidence"
                value={`${(
                  latest.peak_confidence *
                  100
                ).toFixed(1)}%`}
              />

              <MetricCard
                label="Episode"
                value={
                  latest.start_date
                }
              />
            </section>

            <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
                <RegimeBadge
                  type={
                    latest.claim_type
                  }
                />

                <h2 className="mt-5 text-2xl font-semibold">
                  {latest.headline}
                </h2>

                <p className="mt-3 max-w-2xl leading-7 text-zinc-400">
                  This research result comes
                  from the deterministic
                  revision-aware pipeline,
                  not from an LLM.
                </p>

                <Link
                  href={`/episodes/${latest.start_date}`}
                  className="mt-6 inline-flex rounded-xl border border-zinc-700 px-4 py-2 text-sm text-zinc-200 transition hover:bg-zinc-900"
                >
                  Inspect evidence
                </Link>
              </div>

              <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
                <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                  How it works
                </div>

                <div className="mt-6 space-y-5">
                  <div>
                    <div className="font-medium">
                      1. Reconstruct
                    </div>
                    <p className="mt-1 text-sm leading-6 text-zinc-500">
                      Rebuild the economic
                      information available at
                      a historical date.
                    </p>
                  </div>

                  <div>
                    <div className="font-medium">
                      2. Detect
                    </div>
                    <p className="mt-1 text-sm leading-6 text-zinc-500">
                      Apply normalized,
                      direction-aligned regime
                      scoring and episode logic.
                    </p>
                  </div>

                  <div>
                    <div className="font-medium">
                      3. Explain
                    </div>
                    <p className="mt-1 text-sm leading-6 text-zinc-500">
                      Let the assistant explain
                      only validated research
                      outputs and provenance.
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </>
        ) : null}

        <section className="py-12">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                Research episodes
              </div>

              <h2 className="mt-2 text-2xl font-semibold">
                Historical regimes
              </h2>
            </div>

            <div className="text-sm text-zinc-500">
              {data.count} total
            </div>
          </div>

          <div className="space-y-3">
            {data.episodes.map(
              (episode) => (
                <Link
                  key={
                    episode.episode_id
                  }
                  href={`/episodes/${episode.start_date}`}
                  className="grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5 transition hover:border-zinc-600 md:grid-cols-[180px_1fr_150px]"
                >
                  <div className="font-mono text-sm text-zinc-400">
                    {
                      episode.start_date
                    }
                  </div>

                  <div>
                    <div className="font-medium text-zinc-100">
                      {
                        episode.headline
                      }
                    </div>

                    <div className="mt-2">
                      <RegimeBadge
                        type={
                          episode.claim_type
                        }
                      />
                    </div>
                  </div>

                  <div className="text-right font-mono text-sm text-zinc-400">
                    {episode.score.toFixed(
                      3,
                    )}
                  </div>
                </Link>
              ),
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
