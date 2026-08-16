"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type Props = {
  mode?: string;
};

const items = [
  {
    href: "/",
    label: "OVERVIEW",
    active: (path: string) =>
      path === "/",
  },
  {
    href: "/replay",
    label: "REPLAY",
    active: (path: string) =>
      path.startsWith("/replay"),
  },
  {
    href: "/methodology",
    label: "METHODOLOGY",
    active: (path: string) =>
      path.startsWith(
        "/methodology",
      ),
  },
];

function locationLabel(
  pathname: string,
) {
  if (
    pathname.startsWith(
      "/episodes/",
    )
  ) {
    return "EPISODE INSPECTOR";
  }

  if (
    pathname.startsWith(
      "/replay",
    )
  ) {
    return "REPLAY EXPLORER";
  }

  if (
    pathname.startsWith(
      "/methodology",
    )
  ) {
    return "METHODOLOGY";
  }

  return "OVERVIEW";
}

export function AppNav({
  mode,
}: Props) {
  const pathname =
    usePathname();

  return (
    <header className="border-b border-[#242622] bg-[#0d0e0c]">
      <div className="desktop-shell">
        <div className="flex min-h-14 flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-7">
            <Link
              href="/"
              className="text-[11px] font-bold tracking-[0.22em] text-zinc-100"
            >
              LABORLENS
            </Link>

            <nav className="flex items-center gap-1">
              {items.map(
                (item) => {
                  const active =
                    item.active(
                      pathname,
                    );

                  return (
                    <Link
                      key={
                        item.href
                      }
                      href={
                        item.href
                      }
                      aria-current={
                        active
                          ? "page"
                          : undefined
                      }
                      className={[
                        "border-b px-3 py-5 text-[10px] font-bold tracking-[0.11em] transition",
                        active
                          ? "border-[#d6b45d] text-[#e9e7df]"
                          : "border-transparent text-zinc-600 hover:text-zinc-300",
                      ].join(
                        " ",
                      )}
                    >
                      {
                        item.label
                      }
                    </Link>
                  );
                },
              )}

              <a
                href="https://laborlens.onrender.com/docs"
                target="_blank"
                rel="noreferrer"
                className="border-b border-transparent px-3 py-5 text-[10px] font-bold tracking-[0.11em] text-zinc-600 transition hover:text-zinc-300"
              >
                API
              </a>

              <a
                href="https://github.com/namtran1812/laborlens"
                target="_blank"
                rel="noreferrer"
                className="border-b border-transparent px-3 py-5 text-[10px] font-bold tracking-[0.11em] text-zinc-600 transition hover:text-zinc-300"
              >
                SOURCE
              </a>
            </nav>
          </div>

          <div className="flex items-center gap-5 text-[9px] tracking-[0.11em] text-zinc-600">
            <span className="flex items-center gap-2">
              <span className="status-light status-green" />
              API ONLINE
            </span>

            {mode ? (
              <span>
                MODE:
                {mode.toUpperCase()}
              </span>
            ) : null}
          </div>
        </div>
      </div>

      <div className="border-t border-[#1b1d19] bg-[#0a0b09]">
        <div className="desktop-shell flex h-7 items-center justify-between text-[9px] tracking-[0.12em] text-zinc-700">
          <span>
            LABORLENS /{" "}
            <span className="text-zinc-500">
              {locationLabel(
                pathname,
              )}
            </span>
          </span>

          <span>
            {pathname}
          </span>
        </div>
      </div>
    </header>
  );
}
