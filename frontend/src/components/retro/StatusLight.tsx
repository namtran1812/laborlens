type Props = {
  status:
    | "green"
    | "amber"
    | "red";
  label: string;
};

export function StatusLight({
  status,
  label,
}: Props) {
  return (
    <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.1em]">
      <span
        className={[
          "status-light",
          status === "green"
            ? "status-green"
            : status === "amber"
              ? "status-amber"
              : "status-red",
        ].join(" ")}
      />

      <span>{label}</span>
    </div>
  );
}
