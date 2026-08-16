import type {
  ReactNode,
} from "react";

type Props = {
  title: string;
  children: ReactNode;
  className?: string;
  status?: string;
  darkTitle?: boolean;
};

export function Window({
  title,
  children,
  className = "",
  status,
  darkTitle = false,
}: Props) {
  return (
    <section
      className={`retro-window ${className}`}
    >
      <div
        className={[
          darkTitle
            ? "retro-titlebar-dark"
            : "retro-titlebar",
          "flex items-center justify-between px-3",
        ].join(" ")}
      >
        <div className="flex items-center gap-2">
          <span
            className={[
              "h-2.5 w-2.5 border",
              darkTitle
                ? "border-zinc-500 bg-zinc-700"
                : "border-zinc-700 bg-zinc-300",
            ].join(" ")}
          />

          <span className="text-[10px] font-bold uppercase tracking-[0.14em]">
            {title}
          </span>
        </div>

        {status ? (
          <span className="text-[9px] uppercase tracking-[0.12em] opacity-60">
            {status}
          </span>
        ) : null}
      </div>

      <div className="p-4">
        {children}
      </div>
    </section>
  );
}
