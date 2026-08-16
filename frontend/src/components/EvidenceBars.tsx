import type { EvidenceSignal } from "@/lib/api";

type Props = {
  signals: EvidenceSignal[];
};

export function EvidenceBars({
  signals,
}: Props) {
  const max = Math.max(
    ...signals.map((item) =>
      Math.abs(item.contribution),
    ),
    1,
  );

  return (
    <div className="space-y-5">
      {signals.map((signal) => {
        const width =
          (Math.abs(signal.contribution) / max) *
          100;

        return (
          <div key={signal.series_id}>
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-zinc-200">
                {signal.series_id}
              </span>
              <span className="font-mono text-zinc-400">
                {signal.contribution.toFixed(2)}
              </span>
            </div>

            <div className="h-2 overflow-hidden rounded-full bg-zinc-900">
              <div
                className="h-full rounded-full bg-zinc-300"
                style={{
                  width: `${width}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
