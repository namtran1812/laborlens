"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type Props = {
  mode?: string;
};

const tabs = [
  {
    href: "/",
    label: "OVERVIEW",
    active: (path: string) => path === "/",
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
      path.startsWith("/methodology"),
  },
];

export function AppNav({
  mode,
}: Props) {
  const pathname = usePathname();

  return (
    <>
      <div className="workspace-tabs">
        {tabs.map((tab) => {
          const active = tab.active(pathname);

          return (
            <Link
              key={tab.href}
              href={tab.href}
              aria-current={
                active ? "page" : undefined
              }
              className={[
                "workspace-tab",
                active
                  ? "workspace-tab-active"
                  : "",
              ].join(" ")}
            >
              {tab.label}
            </Link>
          );
        })}

        <a
          href="https://laborlens.onrender.com/docs"
          target="_blank"
          rel="noreferrer"
          className="workspace-tab"
        >
          API
        </a>

        <a
          href="https://github.com/namtran1812/laborlens"
          target="_blank"
          rel="noreferrer"
          className="workspace-tab"
        >
          SOURCE
        </a>
      </div>
    </>
  );
}
