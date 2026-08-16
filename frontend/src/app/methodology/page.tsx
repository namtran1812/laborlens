import type {
  Metadata,
} from "next";

import { AppNav } from "@/components/AppNav";
import { DemoNotice } from "@/components/DemoNotice";
import { Window } from "@/components/retro/Window";
import { getMeta } from "@/lib/api";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How LaborLens performs point-in-time reconstruction, regime detection, evidence validation, release-aware replay, and grounded AI interpretation.",
};

const sections = [
  {
    id: "01",
    title: "Point-in-time data",
    body:
      "Economic observations can be revised. LaborLens models realtime_start and realtime_end so historical analysis only uses values available at the selected information date.",
  },
  {
    id: "02",
    title: "Statistical detection",
    body:
      "Indicators are normalized against rolling history, direction-aligned, combined, smoothed, and clustered into episodes. The LLM does not create the regime label.",
  },
  {
    id: "03",
    title: "Evidence and skeptic",
    body:
      "Each detected episode is paired with supporting and opposing evidence. A deterministic skeptic layer evaluates whether the proposed research claim is supported.",
  },
  {
    id: "04",
    title: "Release-aware replay",
    body:
      "LaborLens reruns historical analysis at actual release information dates to measure first detection, revision drift, claim persistence, and which releases changed the available evidence.",
  },
  {
    id: "05",
    title: "Grounded AI",
    body:
      "AI sits after the research boundary. It receives a structured validated research object and explains it. It does not determine the underlying economic result.",
  },
  {
    id: "06",
    title: "Limitations",
    body:
      "LaborLens detects statistical regimes and revision behavior. It does not establish causality, provide investment advice, or claim forecasting accuracy from historical detection alone.",
  },
];

export default async function MethodologyPage() {
  const meta = await getMeta();

  return (
    <main className="min-h-screen pb-10">
      <AppNav mode={meta.mode} />

      <div className="desktop-shell py-5">
        <DemoNotice mode={meta.mode} />

        <Window
          title="LaborLens Help Viewer"
          status="methodology"
          className="mt-5"
          darkTitle
        >
          <div className="grid min-h-[650px] lg:grid-cols-[250px_1fr]">
            <aside className="retro-inset p-3">
              <div className="retro-label px-2 py-2">
                Contents
              </div>

              <nav className="mt-2 space-y-1">
                {sections.map(
                  (section) => (
                    <a
                      key={section.id}
                      href={`#method-${section.id}`}
                      className="block border border-transparent px-2 py-2 text-xs text-zinc-400 hover:border-zinc-700 hover:bg-[#161713] hover:text-zinc-100"
                    >
                      {section.id}.{" "}
                      {section.title}
                    </a>
                  ),
                )}
              </nav>

              <div className="console-rule my-4" />

              <div className="window-help px-2">
                SOURCE
                <br />
                LaborLens research engine
                <br />
                <br />
                MODE
                <br />
                {meta.mode.toUpperCase()}
              </div>
            </aside>

            <article className="px-5 py-4 lg:px-8">
              <div className="retro-label">
                Methodology / document 01
              </div>

              <h1 className="mt-4 text-3xl font-bold text-zinc-100 md:text-5xl">
                Research before narrative.
              </h1>

              <p className="mt-5 max-w-3xl text-sm leading-7 text-zinc-400">
                LaborLens separates
                point-in-time reconstruction,
                statistical detection,
                evidence validation, and AI
                interpretation into distinct
                layers.
              </p>

              <div className="console-rule my-7" />

              <div className="space-y-8">
                {sections.map(
                  (section) => (
                    <section
                      key={section.id}
                      id={`method-${section.id}`}
                    >
                      <div className="flex gap-4">
                        <span className="text-[#d2ad58]">
                          {section.id}
                        </span>

                        <div>
                          <h2 className="text-lg font-bold text-zinc-100">
                            {section.title}
                          </h2>

                          <p className="mt-3 max-w-3xl text-sm leading-7 text-zinc-400">
                            {section.body}
                          </p>
                        </div>
                      </div>

                      <div className="console-rule mt-7" />
                    </section>
                  ),
                )}
              </div>
            </article>
          </div>
        </Window>
      </div>
    </main>
  );
}
