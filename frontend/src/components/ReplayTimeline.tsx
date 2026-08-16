import type { ReplayState } from "@/lib/api";

type Props = {
  states: ReplayState[];
  firstDetected: string | null;
};

export function ReplayTimeline({
  states,
  firstDetected,
}: Props) {
  const detectedScores = states
    .filter(
      (
        state,
      ): state is ReplayState & {
        episode: NonNullable<
          ReplayState["episode"]
        >;
      } => state.episode !== null,
    )
    .map((state) =>
      Math.abs(state.episode.score),
    );

  const maxScore = Math.max(
    ...detectedScores,
    0.001,
  );

  return (
    <div className="space-y-2">
      {states.map((state) => {
        const episode = state.episode;
        const isFirst =
          state.as_of_date === firstDetected;

        const width = episode
          ? Math.max(
              5,
              (Math.abs(episode.score) /
                maxScore) *
                100,
            )
          : 0;

        return (
          <div
            key={state.as_of_date}
            className={[
              "grid gap-4 rounded-xl border p-4",
              "md:grid-cols-[130px_130px_1fr_90px]",
              isFirst
                ? "border-amber-700 bg-amber-950/20"
                : "border-zinc-900 bg-zinc-950",
            ].join(" ")}
          >
            <div className="font-mono text-xs text-zinc-500">
              {state.as_of_date}
            </div>

            <div>
              {state.detected ? (
                <span
                  className={[
                    "text-xs font-medium uppercase tracking-wider",
                    isFirst
                      ? "text-amber-300"
                      : "text-emerald-400",
                  ].join(" ")}
                >
                  {isFirst
                    ? "first detected"
                    : "detected"}
                </span>
              ) : (
                <span className="text-xs uppercase tracking-wider text-zinc-600">
                  not detected
                </span>
              )}
            </div>

            <div className="flex items-center">
              {episode ? (
                <div className="h-1.5 w-full rounded-full bg-zinc-900">
                  <div
                    className="h-full rounded-full bg-zinc-300"
                    style={{
                      width: `${width}%`,
                    }}
                  />
                </div>
              ) : (
                <div className="h-px w-full bg-zinc-900" />
              )}
            </div>

            <div className="text-right font-mono text-sm text-zinc-400">
              {episode
                ? episode.score.toFixed(3)
                : "—"}
            </div>
          </div>
        );
      })}
    </div>
  );
}
