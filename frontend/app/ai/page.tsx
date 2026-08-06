import type { Metadata } from "next";

import AIConversationExperience from "@/components/AIConversationExperience";
import { askAssistant } from "@/services/ai.service";

export const metadata: Metadata = {
  title: "Buying Assistant",
  description: "Describe your needs and get AI-guided product recommendations in seconds.",
  alternates: {
    canonical: "/ai",
  },
};

type Props = {
  searchParams: Promise<{
    q?: string;
  }>;
};

export default async function AIPage({ searchParams }: Props) {
  const { q = "" } = await searchParams;

  const initialResponse = q.trim() ? await askAssistant(q, undefined, 6) : null;

  return (
    <AIConversationExperience
      initialQuery={q}
      initialWorkflow={initialResponse?.workflow ?? null}
      initialAssistantReply={initialResponse?.reply ?? ""}
      initialSessionId={initialResponse?.sessionId}
    />
  );
}