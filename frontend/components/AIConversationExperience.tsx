"use client";

import { useEffect, useState } from "react";

import ProductCard from "@/components/ProductCard";
import { askAssistant } from "@/services/ai.service";
import type { AssistantMessageResponse, RecommendationWorkflow } from "@/types/ai";

const AI_SESSION_KEY = "letrusto:ai-session-id";

type Props = {
  initialQuery: string;
  initialWorkflow: RecommendationWorkflow | null;
  initialAssistantReply: string;
  initialSessionId?: string;
};

export default function AIConversationExperience({
  initialQuery,
  initialWorkflow,
  initialAssistantReply,
  initialSessionId,
}: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [sessionId, setSessionId] = useState<string | undefined>(() => {
    if (typeof window === "undefined") {
      return initialSessionId;
    }

    return window.localStorage.getItem(AI_SESSION_KEY) ?? initialSessionId;
  });
  const [workflow, setWorkflow] = useState<RecommendationWorkflow | null>(initialWorkflow);
  const [assistantReply, setAssistantReply] = useState<string>(initialAssistantReply);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initialSessionId) {
      return;
    }

    window.localStorage.setItem(AI_SESSION_KEY, initialSessionId);
  }, [initialSessionId]);

  const ranked = workflow?.rankedRecommendations ?? [];
  const topProducts = ranked.map((item) => item.product);

  async function handleAsk(nextQuery?: string) {
    const message = (nextQuery ?? query).trim();
    if (!message) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response: AssistantMessageResponse = await askAssistant(message, sessionId, 6);
      setWorkflow(response.workflow);
      setAssistantReply(response.reply);
      setSessionId(response.sessionId);
      window.localStorage.setItem(AI_SESSION_KEY, response.sessionId);
      setQuery(message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to get assistant response.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 py-16 px-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">
          🤖 LeTrusto AI Recommendation
        </h1>

        <p className="text-gray-500 mb-6">
          Ask naturally about budget, use-case, and category. The assistant remembers session context for follow-up questions.
        </p>

        <div className="rounded-3xl border border-purple-100 bg-white p-6 shadow-sm">
          <textarea
            rows={4}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Example: Need a laptop under 80000 for coding and battery life"
            className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-purple-400"
          />

          <button
            type="button"
            onClick={() => void handleAsk()}
            disabled={isLoading}
            className="mt-4 w-full rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-6 py-3 font-semibold text-white transition hover:from-fuchsia-700 hover:to-purple-700 disabled:opacity-60"
          >
            {isLoading ? "Thinking..." : "Ask LeTrusto AI"}
          </button>

          {error ? (
            <p className="mt-4 text-sm text-rose-600">{error}</p>
          ) : null}
        </div>

        {workflow ? (
          <section className="mt-8 rounded-3xl border border-purple-100 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">AI Understanding</h2>
            <p className="mt-3 text-gray-700">{assistantReply || workflow.explanation}</p>

            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              {workflow.intent.category ? (
                <span className="rounded-full bg-purple-100 px-3 py-1 font-semibold text-purple-700">Category: {workflow.intent.category}</span>
              ) : null}
              {workflow.intent.usage ? (
                <span className="rounded-full bg-indigo-100 px-3 py-1 font-semibold text-indigo-700">Usage: {workflow.intent.usage}</span>
              ) : null}
              {workflow.intent.budgetMax ? (
                <span className="rounded-full bg-emerald-100 px-3 py-1 font-semibold text-emerald-700">Budget: up to ₹{workflow.intent.budgetMax.toLocaleString()}</span>
              ) : null}
              {workflow.intent.priorities.map((priority) => (
                <span key={priority} className="rounded-full bg-amber-100 px-3 py-1 font-semibold text-amber-700">
                  Priority: {priority}
                </span>
              ))}
            </div>

            {workflow.followUpQuestions.length > 0 ? (
              <div className="mt-5">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-400">Follow-up prompts</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {workflow.followUpQuestions.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => void handleAsk(question)}
                      className="rounded-full border border-gray-200 px-3 py-1 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </section>
        ) : null}

        <section className="mt-10">
          <div className="mb-4 flex items-end justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Ranked Recommendations</h2>
          </div>

          {topProducts.length > 0 ? (
            <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
              {ranked.map((item) => (
                <div key={item.product.id}>
                  <ProductCard
                    product={item.product}
                    highlightLabel={`AI Score ${item.score.toFixed(1)}`}
                    priority={item.product.id === ranked[0]?.product.id}
                  />
                  <ul className="mt-3 space-y-1 px-2 text-sm text-gray-600">
                    {item.reasons.map((reason) => (
                      <li key={`${item.product.id}-${reason}`}>• {reason}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-3xl border border-dashed border-purple-200 bg-white p-10 text-center shadow-sm">
              <p className="text-gray-600">Ask the assistant to generate ranked recommendations.</p>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
