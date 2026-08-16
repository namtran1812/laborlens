import Link from "next/link";

import { AppNav } from "@/components/AppNav";
import { AskLaborLens } from "@/components/AskLaborLens";
import { DemoNotice } from "@/components/DemoNotice";
import { EvidenceBars } from "@/components/EvidenceBars";
import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import {
  getArticle,
  getEpisode,
  getMeta,
} from "@/lib/api";

type Props = {
  params: Promise<{
    startDate: string;
  }>;
};

export default async function EpisodePage({
  params,
}: Props) {
  const { startDate } =
    await params;

  const [
    detail,
    article,
    meta,
  ] = await Promise.all([
    getEpisode(startDate),
    getArticle(startDate),
    getMeta(),
  ]);

  const episode =
    detail.episode;

  return (
    <main className="min-h-screen bg-black text-white">
      <AppNav mode={meta.mode} />

      <div className="mx-auto max-w-6xl px-6 py-12">
        <DemoNotice
          mode={meta.mode}
        />

        <div className="mt-8">
          <Link
            href="/"
            className="text-sm text-zinc-500 transition hover:text-zinc-200"
          >
            ← Overview
          </Link>
        </div>

        <header className="mt-8 border-b border-zinc-800 pb-10">
          <RegimeBadge
            type={episode.claim_type}
          />

          <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight md:text-5xl">
            {episode.headline}
          </h1>

          <p className="mt-4 font-mono text-sm text-zinc-500">
            {episode.start_date}
            {" → "}
            {episode.end_date}
          </p>
        </header>

        <section className="grid gap-4 py-10 md:grid-cols-4">
          <MetricCard
            label="Regime score"
            value={episode.score.toFixed(
              3,
            )}
          />

          <MetricCard
            label="Confidence"
            value={`${(
              episode.peak_confidence *
              100
            ).toFixed(1)}%`}
          />

          <MetricCard
            label="Skeptic"
            value={
              detail.skeptic.verdict
            }
            detail={`score ${detail.skeptic.score.toFixed(
              3,
            )}`}
          />

          <MetricCard
            label="Historical percentile"
            value={`${(
              detail.historical_percentile *
              100
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

            <p className="mt-3 text-sm leading-6 text-zinc-500">
              Contributions are
              standardized directional
              research signals, not
              percentage changes in the
              raw economic series.
            </p>

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
                  {
                    detail.provenance_rows
                  }
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
                  {
                    detail.evidence
                      .counter.length
                  }
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
          <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
            Grounded research brief
          </div>

          <div className="mt-6 whitespace-pre-wrap text-sm leading-7 text-zinc-300">
            {article.article}
          </div>
        </section>

        <div className="mt-8">
          <AskLaborLens
            startDate={startDate}
            suggestedQuestions={
              meta.suggested_questions
            }
          />
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href={`/replay?target=${startDate}&from=2024-06-01&to=2024-09-01`}
            className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
          >
            Replay this episode
          </Link>

          <Link
            href="/methodology"
            className="rounded-xl border border-zinc-700 px-5 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900"
          >
            Read methodology
          </Link>
        </div>
      </div>
    </main>
  );
}
