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
}: Props) {
  return (
    <section
      className={`retro-window ${className}`}
    >
      <header className="retro-titlebar flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <span className="h-[6px] w-[6px] bg-zinc-600" />

          <span className="text-[9px] font-bold uppercase">
            {title}
          </span>
        </div>

        {status ? (
          <span className="text-[8px] uppercase text-zinc-700">
            {status}
          </span>
        ) : null}
      </header>

      <div className="p-5">
        {children}
      </div>
    </section>
  );
}
