import Link from "next/link";

import { AppNav } from "@/components/AppNav";
import { AskLaborLens } from "@/components/AskLaborLens";
import { DemoNotice } from "@/components/DemoNotice";
import { EvidenceBars } from "@/components/EvidenceBars";
import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import { Window } from "@/components/retro/Window";
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

        <Window
          title={`Episode Inspector : ${startDate}`}
          status="validated"
          className="mt-5"
          darkTitle
        >
          <header className="py-3">
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
        </Window>

        <Window
          title="Research Metrics"
          className="mt-5"
        >
          <section className="grid gap-3 md:grid-cols-4">
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
        </Window>

        <section className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <Window
            title="Evidence Monitor"
            status="supporting"
          >
            <div className="retro-label">
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
          </Window>

          <Window
            title="Research Integrity"
            status="verified"
          >
            <div className="retro-label">
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
          </Window>
        </section>

        <Window
          title="Grounded Research Brief"
          status="deterministic"
          className="mt-5"
        >
          <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
            Grounded research brief
          </div>

          <div className="mt-6 whitespace-pre-wrap text-sm leading-7 text-zinc-300">
            {article.article}
          </div>
        </Window>

        <div className="mt-5">
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
            className="retro-button"
          >
            Replay this episode
          </Link>

          <Link
            href="/methodology"
            className="retro-button retro-button-dark"
          >
            Read methodology
          </Link>
        </div>
      </div>
    </main>
  );
}
