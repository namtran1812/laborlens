export default function Loading() {
  return (
    <main className="min-h-screen">
      <div className="retro-window desktop-shell mt-4">
        <div className="retro-titlebar-dark flex min-h-11 items-center justify-between px-4">
          <span className="text-[11px] font-bold tracking-[0.2em]">
            LABORLENS
          </span>

          <span className="flex items-center gap-2 text-[9px] tracking-[0.12em] text-zinc-400">
            <span className="status-light status-amber" />
            PROCESSING
          </span>
        </div>

        <div className="border-t border-[#8b867a] bg-[#b8b3a8] px-3 py-1.5 text-[9px] uppercase tracking-[0.14em] text-[#45463f]">
          LOCATION: LOADING RESEARCH WORKSPACE
        </div>
      </div>

      <div className="desktop-shell py-5">
        <section className="retro-window">
          <div className="retro-titlebar flex items-center justify-between px-3">
            <span className="text-[10px] font-bold uppercase tracking-[0.14em]">
              Research Process
            </span>

            <span className="text-[9px] uppercase opacity-60">
              please wait
            </span>
          </div>

          <div className="grid min-h-[420px] place-items-center p-8">
            <div className="w-full max-w-xl">
              <div className="retro-inset p-6">
                <div className="flex items-center gap-3">
                  <span className="status-light status-amber animate-pulse" />

                  <span className="text-xs font-bold uppercase tracking-[0.12em] text-zinc-300">
                    Reconstructing information state
                  </span>
                </div>

                <div className="mt-6 space-y-3 font-mono text-[11px] text-zinc-500">
                  <div>
                    &gt; requesting research data...
                  </div>

                  <div>
                    &gt; validating episode state...
                  </div>

                  <div>
                    &gt; loading provenance...
                  </div>

                  <div className="text-[#d2ad58]">
                    &gt; rendering workspace_
                  </div>
                </div>

                <div className="mt-7 h-3 border border-zinc-700 bg-[#050604] p-[2px]">
                  <div className="h-full w-2/3 animate-pulse bg-[#d2ad58]" />
                </div>
              </div>

              <p className="mt-4 text-center text-[9px] uppercase tracking-[0.14em] text-zinc-600">
                LaborLens point-in-time research engine
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
