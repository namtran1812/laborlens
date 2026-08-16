type Props = {
  type: string;
};

export function RegimeBadge({ type }: Props) {
  const contraction = type.includes("contraction");

  return (
    <span
      className={[
        "inline-flex rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-wider",
        contraction
          ? "border-rose-900/70 bg-rose-950/40 text-rose-300"
          : "border-emerald-900/70 bg-emerald-950/40 text-emerald-300",
      ].join(" ")}
    >
      {type.replaceAll("_", " ")}
    </span>
  );
}
