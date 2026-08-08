import type { Metadata } from "next";

import AIConversationExperience from "@/components/AIConversationExperience";
import { askAssistant } from "@/services/ai.service";

export const metadata: Metadata = {
  title: "Buying Assistant",
  description: "Describe your needs and get AI-guided product recommendations in seconds.",
  alternates: {
    canonical: "/ai",
  },
  openGraph: {
    title: "Buying Assistant",
    description: "Describe your needs and get AI-guided product recommendations in seconds.",
    url: "/ai",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Buying Assistant",
    description: "Describe your needs and get AI-guided product recommendations in seconds.",
    images: ["/images/og-default.svg"],
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