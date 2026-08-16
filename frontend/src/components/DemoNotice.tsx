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
    <div className="rounded-2xl border border-amber-900/50 bg-amber-950/20 p-4 text-sm leading-6 text-amber-200/80">
      Public demo mode uses a validated frozen
      historical research snapshot. The full
      repository supports live FRED/ALFRED
      ingestion, ClickHouse point-in-time
      reconstruction, and local AI inference.
    </div>
  );
}
