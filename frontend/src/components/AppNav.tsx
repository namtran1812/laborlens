"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { StatusLight } from "@/components/retro/StatusLight";

type Props = {
  mode?: string;
};

const items = [
  {
    href: "/",
    label: "OVERVIEW",
    match: (path: string) => path === "/",
  },
  {
    href: "/replay",
    label: "REPLAY",
    match: (path: string) =>
      path.startsWith("/replay"),
  },
  {
    href: "/methodology",
    label: "METHOD",
    match: (path: string) =>
      path.startsWith("/methodology"),
  },
];

function pageLabel(
  pathname: string,
): string {
  if (
    pathname.startsWith("/episodes/")
  ) {
    return "RESEARCH / EPISODE INSPECTOR";
  }

  if (
    pathname.startsWith("/replay")
  ) {
    return "RESEARCH / REPLAY CONSOLE";
  }

  if (
    pathname.startsWith("/methodology")
  ) {
    return "HELP / METHODOLOGY";
  }

  return "RESEARCH / OVERVIEW";
}

export function AppNav({
  mode,
}: Props) {
  const pathname = usePathname();

  return (
    <>
      <header className="retro-window desktop-shell mt-4">
        <div className="flex flex-col">
          <div className="flex min-h-11 flex-col md:flex-row md:items-stretch md:justify-between">
            <div className="flex min-w-0 flex-1 items-stretch">
              <Link
                href="/"
                className="retro-titlebar-dark flex items-center px-4 text-[11px] font-bold tracking-[0.2em]"
              >
                LABORLENS
              </Link>

              <nav className="flex min-w-0 flex-wrap items-stretch">
                {items.map((item) => {
                  const active =
                    item.match(pathname);

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      aria-current={
                        active
                          ? "page"
                          : undefined
                      }
                      className={[
                        "flex items-center border-r border-[#aaa598] px-4 py-2 text-[10px] font-bold tracking-[0.11em]",
                        active
                          ? "bg-[#20211d] text-[#f4efe4]"
                          : "bg-[#d5d0c4] text-[#555249] hover:bg-[#e5dfd2] hover:text-[#171714]",
                      ].join(" ")}
                    >
                      {active ? (
                        <span className="mr-2 text-[#d2ad58]">
                          ▸
                        </span>
                      ) : null}

                      {item.label}
                    </Link>
                  );
                })}

                <a
                  href="https://laborlens.onrender.com/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center border-r border-[#aaa598] bg-[#d5d0c4] px-4 py-2 text-[10px] font-bold tracking-[0.11em] text-[#555249] hover:bg-[#e5dfd2] hover:text-[#171714]"
                >
                  API
                </a>

                <a
                  href="https://github.com/namtran1812/laborlens"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center bg-[#d5d0c4] px-4 py-2 text-[10px] font-bold tracking-[0.11em] text-[#555249] hover:bg-[#e5dfd2] hover:text-[#171714]"
                >
                  SOURCE
                </a>
              </nav>
            </div>

            <div className="flex items-center gap-4 border-t border-[#8b867a] bg-[#d5d0c4] px-4 py-2 text-[#555249] md:border-l md:border-t-0">
              <StatusLight
                status="green"
                label="API ONLINE"
              />

              {mode ? (
                <span className="text-[9px] uppercase tracking-[0.12em]">
                  MODE:{mode}
                </span>
              ) : null}
            </div>
          </div>

          <div className="flex items-center justify-between border-t border-[#8b867a] bg-[#b8b3a8] px-3 py-1.5 text-[9px] uppercase tracking-[0.14em] text-[#45463f]">
            <span>
              LOCATION:{" "}
              {pageLabel(pathname)}
            </span>

            <span className="hidden sm:inline">
              PATH: {pathname}
            </span>
          </div>
        </div>
      </header>
    </>
  );
}
