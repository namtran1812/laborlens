type Props = {
  mode: string;
};

export function DemoNotice({
  mode,
}: Props) {
  if (mode !== "demo") {
    return null;
  }

  return (
    <div className="retro-window">
      <div className="retro-titlebar-dark flex items-center justify-between px-3">
        <span className="text-[10px] uppercase tracking-[0.14em]">
          system message
        </span>

        <span className="flex items-center gap-2 text-[9px] uppercase text-zinc-400">
          <span className="status-light status-amber" />
          demo snapshot
        </span>
      </div>

      <div className="flex gap-3 bg-[#17150e] px-4 py-3 text-xs leading-6 text-[#d2ad58]">
        <span>&gt;</span>

        <span>
          Hosted mode uses a validated frozen
          historical research snapshot. Full
          FRED/ALFRED ingestion, ClickHouse
          point-in-time reconstruction, and local
          AI inference remain available in the
          repository.
        </span>
      </div>
    </div>
  );
}
