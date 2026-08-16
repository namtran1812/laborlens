"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  askLaborLens,
  type AskResponse,
} from "@/lib/api";

type Props = {
  startDate: string;
  suggestedQuestions: string[];
};

export function AskLaborLens({
  startDate,
  suggestedQuestions,
}: Props) {
  const [question, setQuestion] =
    useState("");

  const [result, setResult] =
    useState<AskResponse | null>(
      null,
    );

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  async function submitQuestion(
    value: string,
  ) {
    const cleaned = value.trim();

    if (!cleaned) {
      return;
    }

    setQuestion(cleaned);
    setLoading(true);
    setError(null);

    try {
      const response =
        await askLaborLens({
          question: cleaned,
          startDate,
        });

      setResult(response);
    } catch (err) {
      setResult(null);

      setError(
        err instanceof Error
          ? err.message
          : "Assistant request failed",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    await submitQuestion(question);
  }

  return (
    <section className="rounded-3xl border border-zinc-800 bg-zinc-950 p-7">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">
            Ask LaborLens
          </div>

          <h2 className="mt-2 text-2xl font-semibold">
            Grounded research assistant
          </h2>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
            Ask questions about this episode.
            Answers are constrained to validated
            LaborLens research results.
          </p>
        </div>

        <span className="rounded-full border border-zinc-800 px-3 py-1 text-xs uppercase tracking-wider text-zinc-500">
          evidence-grounded
        </span>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {suggestedQuestions.map(
          (item) => (
            <button
              key={item}
              type="button"
              onClick={() =>
                submitQuestion(item)
              }
              className="rounded-full border border-zinc-800 px-3 py-2 text-left text-xs text-zinc-400 transition hover:border-zinc-600 hover:text-zinc-200"
            >
              {item}
            </button>
          ),
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="mt-6 flex flex-col gap-3 sm:flex-row"
      >
        <input
          value={question}
          onChange={(event) =>
            setQuestion(
              event.target.value,
            )
          }
          placeholder="Ask about evidence, revisions, detection timing..."
          className="min-w-0 flex-1 rounded-xl border border-zinc-800 bg-black px-4 py-3 text-sm text-zinc-100 outline-none transition placeholder:text-zinc-600 focus:border-zinc-600"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading
            ? "Analyzing..."
            : "Ask"}
        </button>
      </form>

      {error ? (
        <div className="mt-5 rounded-xl border border-rose-900/60 bg-rose-950/20 p-4 text-sm text-rose-300">
          {error}
        </div>
      ) : null}

      {result ? (
        <div className="mt-6 rounded-2xl border border-zinc-800 bg-black p-6">
          <div className="text-sm leading-7 text-zinc-200">
            {result.answer}
          </div>

          <div className="mt-6 border-t border-zinc-900 pt-5">
            <div className="text-xs uppercase tracking-[0.18em] text-zinc-600">
              Grounding sources
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {result.sources.map(
                (source) => (
                  <span
                    key={source}
                    className="rounded-full border border-zinc-800 px-3 py-1 font-mono text-xs text-zinc-500"
                  >
                    {source}
                  </span>
                ),
              )}
            </div>

            <div className="mt-5 grid gap-2 text-xs text-zinc-600 sm:grid-cols-2">
              <div>
                mode: {result.mode}
              </div>
              <div>
                model: {result.model}
              </div>
            </div>

            <p className="mt-4 text-xs leading-5 text-zinc-600">
              {result.caveat}
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}
