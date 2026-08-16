"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & {
    digest?: string;
  };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
      <div className="w-full max-w-xl rounded-3xl border border-zinc-800 bg-zinc-950 p-8">
        <div className="text-xs uppercase tracking-[0.2em] text-rose-400">
          Research service unavailable
        </div>

        <h1 className="mt-4 text-3xl font-semibold">
          LaborLens could not load this view.
        </h1>

        <p className="mt-4 leading-7 text-zinc-400">
          The public backend may be waking
          from an idle state, or the requested
          research object may be temporarily
          unavailable.
        </p>

        <div className="mt-7 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => reset()}
            className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
          >
            Try again
          </button>

          <Link
            href="/"
            className="rounded-xl border border-zinc-700 px-5 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900"
          >
            Return home
          </Link>
        </div>

        {error.digest ? (
          <p className="mt-6 font-mono text-xs text-zinc-700">
            reference: {error.digest}
          </p>
        ) : null}
      </div>
    </main>
  );
}
