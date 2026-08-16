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
    <div className="border-l border-[#34362f] px-4 py-2 first:border-l-0">
      <div className="retro-label">
        {label}
      </div>

      <div className="mt-2 text-lg font-bold text-zinc-100">
        {value}
      </div>

      {detail ? (
        <div className="mt-1 text-[10px] text-zinc-600">
          {detail}
        </div>
      ) : null}
    </div>
  );
}
