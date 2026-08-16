import Link from "next/link";

type Props = {
  mode?: string;
};

export function AppNav({
  mode,
}: Props) {
  return (
    <nav className="border-b border-zinc-900 bg-black/95">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="text-sm font-semibold tracking-[0.2em] text-zinc-100"
          >
            LABORLENS
          </Link>

          {mode ? (
            <span className="ml-4 rounded-full border border-emerald-900/60 bg-emerald-950/20 px-3 py-1 text-[10px] uppercase tracking-[0.15em] text-emerald-400 sm:hidden">
              API live · {mode}
            </span>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-x-5 gap-y-3 text-sm">
          <Link
            href="/"
            className="text-zinc-400 transition hover:text-white"
          >
            Overview
          </Link>

          <Link
            href="/replay"
            className="text-zinc-400 transition hover:text-white"
          >
            Replay
          </Link>

          <Link
            href="/methodology"
            className="text-zinc-400 transition hover:text-white"
          >
            Methodology
          </Link>

          <a
            href="https://laborlens.onrender.com/docs"
            target="_blank"
            rel="noreferrer"
            className="text-zinc-400 transition hover:text-white"
          >
            API
          </a>

          <a
            href="https://github.com/namtran1812/laborlens"
            target="_blank"
            rel="noreferrer"
            className="text-zinc-400 transition hover:text-white"
          >
            GitHub
          </a>

          {mode ? (
            <span className="hidden rounded-full border border-emerald-900/60 bg-emerald-950/20 px-3 py-1 text-[10px] uppercase tracking-[0.15em] text-emerald-400 sm:inline-flex">
              API live · {mode}
            </span>
          ) : null}
        </div>
      </div>
    </nav>
  );
}
