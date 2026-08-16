import Link from "next/link";

import { MetricCard } from "@/components/MetricCard";
import { RegimeBadge } from "@/components/RegimeBadge";
import { ReplayTimeline } from "@/components/ReplayTimeline";
import { getReplay } from "@/lib/api";

type SearchParams = Promise<
  Record<
    string,
    string | string[] | undefined
  >
>;

function value(
  input: string | string[] | undefined,
  fallback: string,
): string {
  return typeof input === "string"
    ? input
    : fallback;
}

export default async function ReplayPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;

  const target = value(
    params.target,
    "2024-06-01",
  );

  const from = value(
    params.from,
    "2024-06-01",
  );

  const to = value(
    params.to,
    "2024-09-01",
  );

  const data = await getReplay({
    from,
    to,
    target,
    schedule: "releases",
  });

  const metrics = data.metrics;
  const reference =
    data.reference_episode;

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <nav className="flex items-center justify-between">
          <Link
            href="/"
            className="text-sm text-zinc-500 transition hover:text-zinc-200"
          >
            ← LaborLens
          </Link>

          <span className="text-xs uppercase tracking-[0.2em] text-zinc-600">
            Release-aware replay
          </span>
        </nav>

        <header className="mt-12 border-b border-zinc-800 pb-10">
          <div className="text-xs uppercase tracking-[0.25em] text-zinc-500">
            Replay explorer
          </div>

          <h1 className="mt-4 max-w-4xl text-4xl font-semibold tracking-tight md:text-6xl">
            What did the data say at the time?
          </h1>

          <p className="mt-5 max-w-3xl text-zinc-400">
            Reconstruct historical information
            states across actual economic
            releases and revisions.
          </p>
        </header>

        <form
          className="my-8 grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5 md:grid-cols-4"
          method="GET"
        >
          <label className="text-sm text-zinc-500">
            Target episode
            <input
              name="target"
              type="date"
              defaultValue={target}
              className="mt-2 w-full rounded-lg border border-zinc-800 bg-black p-3 text-zinc-200"
            />
          </label>

          <label className="text-sm text-zinc-500">
            Replay from
            <input
              name="from"
              type="date"
              defaultValue={from}
              className="mt-2 w-full rounded-lg border border-zinc-800 bg-black p-3 text-zinc-200"
            />
          </label>

          <label className="text-sm text-zinc-500">
            Replay to
            <input
              name="to"
              type="date"
              defaultValue={to}
              className="mt-2 w-full rounded-lg border border-zinc-800 bg-black p-3 text-zinc-200"
            />
          </label>

          <div className="flex items-end">
            <button
              type="submit"
              className="w-full rounded-lg bg-white px-4 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
            >
              Reconstruct
            </button>
          </div>
        </form>

        {reference ? (
          <>
            <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
              <RegimeBadge
                type={
                  reference.claim_type
                }
              />

              <h2 className="mt-5 text-2xl font-semibold">
                {reference.headline}
              </h2>

              <p className="mt-2 font-mono text-sm text-zinc-500">
                {reference.start_date}
                {" → "}
                {reference.end_date}
              </p>
            </section>

            <section className="grid gap-4 py-8 md:grid-cols-4">
              <MetricCard
                label="First detected"
                value={
                  metrics.first_detected_as_of ??
                  "n/a"
                }
                detail={
                  metrics.previous_information_state
                    ? `previous state ${metrics.previous_information_state}`
                    : undefined
                }
              />

              <MetricCard
                label="Detection latency"
                value={
                  metrics.detection_latency_days !==
                  null
                    ? `${metrics.detection_latency_days} d`
                    : "n/a"
                }
              />

              <MetricCard
                label="Survival"
                value={
                  metrics.survival_rate !==
                  null
                    ? `${(
                        metrics.survival_rate *
                        100
                      ).toFixed(1)}%`
                    : "n/a"
                }
              />

              <MetricCard
                label="Score revision"
                value={
                  metrics.absolute_score_revision !==
                  null
                    ? metrics.absolute_score_revision.toFixed(
                        3,
                      )
                    : "n/a"
                }
              />
            </section>

            <section className="grid gap-8 lg:grid-cols-[1.4fr_0.6fr]">
              <div>
                <div className="mb-5">
                  <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                    Information states
                  </div>

                  <h2 className="mt-2 text-2xl font-semibold">
                    Detection timeline
                  </h2>
                </div>

                <ReplayTimeline
                  states={data.states}
                  firstDetected={
                    metrics.first_detected_as_of
                  }
                />
              </div>

              <aside className="space-y-4">
                <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
                  <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                    Detection release
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {metrics
                      .detection_release_series
                      .length ? (
                      metrics
                        .detection_release_series
                        .map((series) => (
                          <span
                            key={series}
                            className="rounded-full border border-zinc-700 px-3 py-1 font-mono text-sm"
                          >
                            {series}
                          </span>
                        ))
                    ) : (
                      <span className="text-zinc-500">
                        none
                      </span>
                    )}
                  </div>
                </div>

                <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
                  <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                    Revision stability
                  </div>

                  <dl className="mt-5 space-y-4 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-zinc-500">
                        Type flips
                      </dt>
                      <dd>
                        {
                          metrics.claim_type_flips
                        }
                      </dd>
                    </div>

                    <div className="flex justify-between">
                      <dt className="text-zinc-500">
                        Start drift
                      </dt>
                      <dd>
                        {metrics.start_drift_months ??
                          "n/a"}{" "}
                        mo
                      </dd>
                    </div>

                    <div className="flex justify-between">
                      <dt className="text-zinc-500">
                        End drift
                      </dt>
                      <dd>
                        {metrics.end_drift_months ??
                          "n/a"}{" "}
                        mo
                      </dd>
                    </div>

                    <div className="flex justify-between">
                      <dt className="text-zinc-500">
                        Replay states
                      </dt>
                      <dd>
                        {
                          metrics.replay_dates
                        }
                      </dd>
                    </div>

                    <div className="flex justify-between">
                      <dt className="text-zinc-500">
                        Detected
                      </dt>
                      <dd>
                        {
                          metrics.detected_states
                        }
                      </dd>
                    </div>
                  </dl>
                </div>
              </aside>
            </section>
          </>
        ) : (
          <div className="rounded-2xl border border-zinc-800 p-8 text-zinc-400">
            No final reference episode was
            found for this target.
          </div>
        )}
      </div>
    </main>
  );
}
