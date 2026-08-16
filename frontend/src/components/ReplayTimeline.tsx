import type {
  ReplayState,
} from "@/lib/api";

type Props = {
  states: ReplayState[];
  firstDetected: string | null;
};

export function ReplayTimeline({
  states,
  firstDetected,
}: Props) {
  return (
    <div className="retro-inset overflow-x-auto">
      <table className="console-table min-w-[620px]">
        <thead>
          <tr>
            <th>Information date</th>
            <th>State</th>
            <th>Regime score</th>
            <th>Confidence</th>
          </tr>
        </thead>

        <tbody>
          {states.map((state) => {
            const episode =
              state.episode;

            const isFirst =
              state.as_of_date ===
              firstDetected;

            return (
              <tr
                key={state.as_of_date}
                className={
                  isFirst
                    ? "bg-[#261f0d]"
                    : ""
                }
              >
                <td className="font-mono text-zinc-400">
                  {state.as_of_date}
                </td>

                <td>
                  <span
                    className={[
                      "font-mono text-[11px] uppercase tracking-[0.08em]",
                      isFirst
                        ? "text-[#d2ad58]"
                        : state.detected
                          ? "text-[#75b978]"
                          : "text-zinc-600",
                    ].join(" ")}
                  >
                    {isFirst
                      ? ">> first detected"
                      : state.detected
                        ? "detected"
                        : "not detected"}
                  </span>
                </td>

                <td className="font-mono text-zinc-300">
                  {episode
                    ? episode.score.toFixed(3)
                    : "---"}
                </td>

                <td className="font-mono text-zinc-500">
                  {episode
                    ? `${(
                        episode.confidence *
                        100
                      ).toFixed(1)}%`
                    : "---"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
