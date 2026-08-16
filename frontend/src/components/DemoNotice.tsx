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
    <div className="mb-5 flex items-start gap-3 border-l-2 border-[#d6b45d] bg-[#11110d] px-4 py-3 text-[11px] leading-5 text-zinc-500">
      <span className="mt-[6px] status-light status-amber" />

      <p>
        Public demo uses a validated
        historical snapshot. The full
        repository supports live
        FRED/ALFRED ingestion,
        ClickHouse point-in-time
        reconstruction, and local AI.
      </p>
    </div>
  );
}
