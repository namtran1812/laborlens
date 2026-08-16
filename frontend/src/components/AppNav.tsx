import Link from "next/link";

import { StatusLight } from "@/components/retro/StatusLight";

type Props = {
  mode?: string;
};

export function AppNav({
  mode,
}: Props) {
  return (
    <header className="retro-window mx-auto mt-4 max-w-7xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex min-h-11 items-center">
          <div className="retro-titlebar flex h-full items-center px-4">
            <Link
              href="/"
              className="text-xs font-bold tracking-[0.18em]"
            >
              LABORLENS
            </Link>
          </div>

          <nav className="flex flex-wrap items-center px-3 py-2 text-[11px] uppercase tracking-[0.08em]">
            <Link
              href="/"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              File
            </Link>

            <Link
              href="/"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              Research
            </Link>

            <Link
              href="/replay"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              Replay
            </Link>

            <Link
              href="/methodology"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              Method
            </Link>

            <a
              href="https://laborlens.onrender.com/docs"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              API
            </a>

            <a
              href="https://github.com/namtran1812/laborlens"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1 hover:bg-zinc-800 hover:text-white"
            >
              Source
            </a>
          </nav>
        </div>

        <div className="flex items-center gap-4 border-t border-zinc-500 px-4 py-2 md:border-l md:border-t-0">
          <StatusLight
            status="green"
            label="API ONLINE"
          />

          {mode ? (
            <div className="text-[10px] uppercase tracking-[0.12em] text-zinc-600">
              MODE:{mode}
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
