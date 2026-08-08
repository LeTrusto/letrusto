"use client";

import { useState } from "react";

import { askAssistant } from "@/services/ai.service";
import type { RecommendationWorkflow } from "@/types/ai";

const AI_SESSION_KEY = "letrusto:ai-session-id";

type Props = {
  initialQuery?: string;
};

export default function AIConversationExperience({ initialQuery = "" }: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [sessionId, setSessionId] = useState<string | undefined>(() => {
    if (typeof window === "undefined") {
      return undefined;
    }

    return window.localStorage.getItem(AI_SESSION_KEY) ?? undefined;
  });
  const [workflow, setWorkflow] = useState<RecommendationWorkflow | null>(null);
  const [assistantReply, setAssistantReply] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(nextQuery?: string) {
    const message = (nextQuery ?? query).trim();
    if (!message) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await askAssistant(message, sessionId, 6);
      setWorkflow(result.workflow);
      setAssistantReply(result.reply);
      setSessionId(result.sessionId);
      setQuery(message);

      if (typeof window !== "undefined") {
        window.localStorage.setItem(AI_SESSION_KEY, result.sessionId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to get assistant response.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_right,_rgba(14,165,233,0.16),_transparent_32%),radial-gradient(circle_at_12%_24%,_rgba(251,191,36,0.18),_transparent_34%),linear-gradient(180deg,#f8fafc_0%,#ffffff_100%)] px-6 py-16">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-4xl font-black tracking-tight text-slate-950">Ask LeTrusto</h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          Describe what you are evaluating and the assistant will help you refine priorities and next steps.
        </p>

        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="block text-sm font-semibold text-slate-800" htmlFor="assistant-query">Your message</label>
          <textarea
            id="assistant-query"
            rows={4}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Example: I need help choosing an AI writing tool for a small team budget"
            className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-sky-500"
          />

          <button
            type="button"
            onClick={() => void handleAsk()}
            disabled={isLoading}
            className="mt-7 w-full rounded-2xl bg-gradient-to-r from-cyan-600 to-sky-600 px-6 py-3.5 font-semibold text-white transition hover:from-cyan-700 hover:to-sky-700 disabled:opacity-60"
          >
            {isLoading ? "Thinking..." : "Ask LeTrusto"}
          </button>

          {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
        </section>

        {assistantReply ? (
          <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Assistant Reply</h2>
            <p className="mt-3 whitespace-pre-wrap text-slate-700">{assistantReply}</p>

            {workflow?.followUpQuestions?.length ? (
              <div className="mt-6">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Follow-up prompts</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {workflow.followUpQuestions.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => void handleAsk(question)}
                      className="rounded-full border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-slate-500"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </section>
        ) : null}
      </div>
    </main>
  );
}
