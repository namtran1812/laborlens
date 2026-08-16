type Props = {
  label: string;
  value: string;
  detail?: string;
};

export function MetricCard({
  label,
  value,
  detail,
}: Props) {
  return (
    <div className="retro-inset p-4">
      <div className="retro-label">
        {label}
      </div>

      <div className="mt-3 font-mono text-xl font-bold text-zinc-100">
        {value}
      </div>

      {detail ? (
        <div className="mt-2 text-[11px] text-zinc-500">
          {detail}
        </div>
      ) : null}
    </div>
  );
}
