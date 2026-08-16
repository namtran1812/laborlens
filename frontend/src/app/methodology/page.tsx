import type { Metadata } from "next";
import { AppNav } from "@/components/AppNav";
import { DemoNotice } from "@/components/DemoNotice";
import { getMeta } from "@/lib/api";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How LaborLens performs point-in-time reconstruction, regime detection, evidence validation, release-aware replay, and grounded AI interpretation.",
};

export default async function MethodologyPage() {
  const meta = await getMeta();

  return (
    <main className="min-h-screen bg-black text-white">
      <AppNav mode={meta.mode} />

      <div className="mx-auto max-w-4xl px-6 py-12">
        <DemoNotice
          mode={meta.mode}
        />

        <header className="mt-10 border-b border-zinc-800 pb-10">
          <div className="text-xs uppercase tracking-[0.25em] text-zinc-500">
            Methodology
          </div>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight md:text-6xl">
            Research before narrative.
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-zinc-400">
            LaborLens separates
            point-in-time reconstruction,
            statistical detection,
            evidence validation, and AI
            interpretation into distinct
            layers.
          </p>
        </header>

        <div className="space-y-8 py-10">
          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              1. Point-in-time data
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              Economic observations can
              be revised. LaborLens models
              realtime_start and
              realtime_end so historical
              analysis only uses values
              that were available at the
              selected information date.
            </p>
          </section>

          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              2. Statistical detection
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              Indicators are normalized
              against rolling history,
              direction-aligned, combined,
              smoothed, and clustered into
              episodes. The LLM does not
              create the regime label.
            </p>
          </section>

          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              3. Evidence and skeptic
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              Each detected episode is
              paired with supporting and
              opposing evidence. A
              deterministic skeptic layer
              evaluates whether the
              proposed research claim is
              supported.
            </p>
          </section>

          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              4. Release-aware replay
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              LaborLens reruns historical
              analysis at actual release
              information dates to measure
              first detection, revision
              drift, claim persistence,
              and which releases changed
              the available evidence.
            </p>
          </section>

          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              5. Grounded AI
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              AI sits after the research
              boundary. It receives a
              structured validated
              research object and explains
              it. It does not determine the
              underlying economic result.
            </p>
          </section>

          <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
            <h2 className="text-2xl font-semibold">
              Limitations
            </h2>

            <p className="mt-4 leading-7 text-zinc-400">
              LaborLens detects statistical
              regimes and revision
              behavior. It does not
              establish causality, provide
              investment advice, or claim
              forecasting accuracy from
              historical detection alone.
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
