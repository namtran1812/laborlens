import Link from "next/link";

import { DemoNotice } from "@/components/DemoNotice";
import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import { Window } from "@/components/retro/Window";
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
    <main className="min-h-[calc(100vh-86px)] pb-10">
      <div className="desktop-shell py-5">
        <DemoNotice mode={meta.mode} />

        <div className="mt-5 grid gap-5 xl:grid-cols-[1.55fr_0.45fr]">
          <Window
            title="Research Overview"
            status="workspace 01"
            darkTitle
          >
            <div className="py-2">
              <div className="retro-label">
                revision-aware economic research
              </div>

              <h1 className="mt-4 max-w-4xl text-3xl font-bold leading-tight tracking-tight text-zinc-100 md:text-5xl">
                What did the labor market
                look like with only the
                information available then?
              </h1>

              <p className="mt-5 max-w-3xl text-sm leading-7 text-zinc-400">
                LaborLens reconstructs historical
                FRED/ALFRED information states,
                detects labor-market regimes,
                measures revision stability, and
                explains validated findings through
                a grounded research assistant.
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href="/replay?target=2024-06-01&from=2024-06-01&to=2024-09-01"
                  className="retro-button"
                >
                  Open replay console
                </Link>

                {latest ? (
                  <Link
                    href={`/episodes/${latest.start_date}`}
                    className="retro-button retro-button-dark"
                  >
                    Open research workspace
                  </Link>
                ) : null}
              </div>
            </div>
          </Window>

          <Window
            title="System Status"
            status="online"
          >
            <dl className="space-y-4 text-xs">
              <div className="flex justify-between gap-4">
                <dt className="text-zinc-500">
                  API
                </dt>
                <dd className="flex items-center gap-2 text-[#75b978]">
                  <span className="status-light status-green" />
                  ONLINE
                </dd>
              </div>

              <div className="console-rule" />

              <div className="flex justify-between gap-4">
                <dt className="text-zinc-500">
                  MODE
                </dt>
                <dd>
                  {meta.mode.toUpperCase()}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-zinc-500">
                  ENGINE
                </dt>
                <dd>POINT-IN-TIME</dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-zinc-500">
                  AI
                </dt>
                <dd>
                  {meta.ai_provider ??
                    "OFFLINE"}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-zinc-500">
                  SERIES
                </dt>
                <dd>FRED/ALFRED</dd>
              </div>
            </dl>
          </Window>
        </div>

        {latest ? (
          <>
            <Window
              title="Current Regime Monitor"
              status={latest.start_date}
              className="mt-5"
            >
              <div className="grid gap-3 md:grid-cols-4">
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
                  label="Observation"
                  value={latest.start_date}
                />
              </div>
            </Window>

            <div className="mt-5 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
              <Window
                title="Detected Episode"
                status="validated"
              >
                <RegimeBadge
                  type={
                    latest.claim_type
                  }
                />

                <h2 className="mt-5 text-xl font-bold text-zinc-100">
                  {latest.headline}
                </h2>

                <p className="mt-3 text-xs leading-6 text-zinc-500">
                  Result generated by the
                  deterministic revision-aware
                  research engine. Narrative
                  generation is downstream of
                  this state.
                </p>

                <Link
                  href={`/episodes/${latest.start_date}`}
                  className="retro-button mt-5"
                >
                  Inspect evidence
                </Link>
              </Window>

              <Window
                title="Pipeline"
                status="3 stages"
              >
                <ol className="space-y-4 text-xs">
                  <li className="grid grid-cols-[28px_1fr] gap-3">
                    <span className="text-[#d2ad58]">
                      01
                    </span>
                    <div>
                      <div className="font-bold">
                        RECONSTRUCT
                      </div>
                      <div className="mt-1 text-zinc-500">
                        Historical information
                        set at time t.
                      </div>
                    </div>
                  </li>

                  <div className="console-rule" />

                  <li className="grid grid-cols-[28px_1fr] gap-3">
                    <span className="text-[#d2ad58]">
                      02
                    </span>
                    <div>
                      <div className="font-bold">
                        DETECT
                      </div>
                      <div className="mt-1 text-zinc-500">
                        Direction-aligned regime
                        scoring and episodes.
                      </div>
                    </div>
                  </li>

                  <div className="console-rule" />

                  <li className="grid grid-cols-[28px_1fr] gap-3">
                    <span className="text-[#d2ad58]">
                      03
                    </span>
                    <div>
                      <div className="font-bold">
                        EXPLAIN
                      </div>
                      <div className="mt-1 text-zinc-500">
                        Grounded interpretation
                        of validated outputs.
                      </div>
                    </div>
                  </li>
                </ol>
              </Window>
            </div>
          </>
        ) : null}

        <Window
          title="Historical Episode Registry"
          status={`${data.count} records`}
          className="mt-5"
        >
          <div className="retro-inset overflow-x-auto">
            <table className="console-table min-w-[700px]">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Classification</th>
                  <th>Headline</th>
                  <th>Score</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {data.episodes.map(
                  (episode) => (
                    <tr
                      key={
                        episode.episode_id
                      }
                    >
                      <td className="font-mono text-zinc-400">
                        {
                          episode.start_date
                        }
                      </td>

                      <td>
                        {episode.claim_type.replaceAll(
                          "_",
                          " ",
                        )}
                      </td>

                      <td className="text-zinc-300">
                        {
                          episode.headline
                        }
                      </td>

                      <td className="font-mono">
                        {episode.score.toFixed(
                          3,
                        )}
                      </td>

                      <td>
                        <Link
                          href={`/episodes/${episode.start_date}`}
                          className="text-[#d2ad58] hover:underline"
                        >
                          OPEN
                        </Link>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </Window>
      </div>
    </main>
  );
}
