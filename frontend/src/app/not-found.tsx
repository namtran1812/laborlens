import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
      <div className="max-w-xl text-center">
        <div className="font-mono text-sm text-zinc-600">
          404
        </div>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Research view not found.
        </h1>

        <p className="mt-4 leading-7 text-zinc-400">
          The requested episode or page is
          not available in this information
          set.
        </p>

        <div className="mt-8 flex justify-center gap-3">
          <Link
            href="/"
            className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black"
          >
            Overview
          </Link>

          <Link
            href="/replay"
            className="rounded-xl border border-zinc-700 px-5 py-3 text-sm text-zinc-300"
          >
            Replay explorer
          </Link>
        </div>
      </div>
    </main>
  );
}
