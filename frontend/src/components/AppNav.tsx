import Link from "next/link";

type Props = {
  mode?: string;
};

export function AppNav({
  mode,
}: Props) {
  return (
    <nav className="border-b border-zinc-900 bg-black/95">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="text-sm font-semibold tracking-[0.2em] text-zinc-100"
        >
          LABORLENS
        </Link>

        <div className="flex items-center gap-5 text-sm">
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

          {mode ? (
            <span className="rounded-full border border-zinc-800 px-3 py-1 text-xs uppercase tracking-[0.15em] text-zinc-500">
              {mode}
            </span>
          ) : null}
        </div>
      </div>
    </nav>
  );
}
