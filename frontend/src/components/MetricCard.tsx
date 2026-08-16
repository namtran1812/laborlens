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
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
      <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">
        {label}
      </div>
      <div className="mt-3 text-2xl font-semibold text-zinc-100">
        {value}
      </div>
      {detail ? (
        <div className="mt-2 text-sm text-zinc-500">
          {detail}
        </div>
      ) : null}
    </div>
  );
}
