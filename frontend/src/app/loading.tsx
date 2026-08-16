export default function Loading() {
  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="animate-pulse">
          <div className="h-3 w-40 rounded bg-zinc-800" />

          <div className="mt-8 h-12 max-w-3xl rounded bg-zinc-900" />

          <div className="mt-4 h-12 max-w-2xl rounded bg-zinc-900" />

          <div className="mt-6 h-5 max-w-xl rounded bg-zinc-900" />

          <div className="mt-12 grid gap-4 md:grid-cols-4">
            {Array.from({
              length: 4,
            }).map((_, index) => (
              <div
                key={index}
                className="h-28 rounded-2xl border border-zinc-900 bg-zinc-950"
              />
            ))}
          </div>

          <div className="mt-8 h-80 rounded-3xl border border-zinc-900 bg-zinc-950" />
        </div>

        <p className="mt-8 font-mono text-xs uppercase tracking-[0.2em] text-zinc-600">
          Reconstructing research state…
        </p>
      </div>
    </main>
  );
}
