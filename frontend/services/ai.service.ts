import { recommendProducts, resolveCompareProducts } from "@/lib/recommendations";
import { products } from "@/lib/products";
import { IS_API_CONFIGURED, apiRequest, buildQueryString } from "@/services/api";
import type {
  AssistantMessageResponse,
  BuyingGuide,
  ComparisonSummary,
  RecommendationWorkflow,
  ReviewSummary,
} from "@/types/ai";
import type { Product } from "@/types/products";

type LocalConversationContext = {
  lastQuery: string;
  lastWorkflow: RecommendationWorkflow | null;
};

const localConversations = new Map<string, LocalConversationContext>();

const GREETING_WORDS = new Set(["hello", "hi", "hey", "hola", "namaste", "good morning", "good evening"]);

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return 0;
}

function normalizeProduct(product: Product): Product {
  return {
    ...product,
    priceValue: toNumber(product.priceValue),
    rating: toNumber(product.rating),
    aiScore: toNumber(product.aiScore),
    priceHistory: product.priceHistory.map((point) => ({
      ...point,
      price: toNumber(point.price),
    })),
    reviews: product.reviews.map((review) => ({
      ...review,
      rating: toNumber(review.rating),
    })),
  };
}

function normalizeWorkflow(workflow: RecommendationWorkflow): RecommendationWorkflow {
  return {
    ...workflow,
    rankedRecommendations: workflow.rankedRecommendations.map((item) => ({
      ...item,
      score: toNumber(item.score),
      product: normalizeProduct(item.product),
    })),
  };
}

function localWorkflowFallback(query: string, limit: number): RecommendationWorkflow {
  const picks = recommendProducts(query, limit).map((product) => normalizeProduct(product));

  return {
    intent: {
      budgetMin: null,
      budgetMax: null,
      usage: null,
      category: null,
      priorities: [],
    },
    explanation: "I ranked these options using product fit, value, and review quality signals.",
    rankedRecommendations: picks.map((product, index) => ({
      product,
      score: Math.max(0, 100 - index * 8),
      reasons: ["Matched against local product metadata and AI score."],
    })),
    followUpQuestions: [
      "What is your budget?",
      "Do you want me to prioritize performance or value?",
    ],
  };
}

function mergeIntent(
  current: RecommendationWorkflow["intent"],
  previous: RecommendationWorkflow["intent"] | null
): RecommendationWorkflow["intent"] {
  if (!previous) {
    return current;
  }

  return {
    budgetMin: current.budgetMin ?? previous.budgetMin,
    budgetMax: current.budgetMax ?? previous.budgetMax,
    usage: current.usage ?? previous.usage,
    category: current.category ?? previous.category,
    priorities: Array.from(new Set([...previous.priorities, ...current.priorities])),
  };
}

function isGreeting(message: string): boolean {
  const normalized = message.trim().toLowerCase();
  return GREETING_WORDS.has(normalized);
}

function buildHeuristicAssistantReply(
  message: string,
  workflow: RecommendationWorkflow,
  previousWorkflow: RecommendationWorkflow | null
): string {
  if (isGreeting(message)) {
    return "Hi! I can help you find the right product quickly. Tell me your budget, category, and use-case, and I will shortlist the best options.";
  }

  const normalized = message.toLowerCase();
  const top = workflow.rankedRecommendations[0]?.product;

  if (normalized.includes("compare") && (normalized.includes("iphone") || normalized.includes("samsung"))) {
    return "For iPhone vs Samsung, iPhone usually leads in long-term software consistency, while Samsung often offers better display and value at the same price tier. Share your budget and I will suggest the stronger pick for your use-case.";
  }

  if (!top) {
    return "I can help with that. Share a budget and preferred category, and I will narrow it down to the best options.";
  }

  const detailParts: string[] = [];
  if (workflow.intent.budgetMax) {
    detailParts.push(`within about ₹${workflow.intent.budgetMax.toLocaleString()}`);
  }
  if (workflow.intent.category) {
    detailParts.push(`in ${workflow.intent.category}`);
  }
  if (workflow.intent.usage) {
    detailParts.push(`for ${workflow.intent.usage}`);
  }

  const contextPrefix = previousWorkflow
    ? "Using your previous preferences and this follow-up, "
    : "Based on your request, ";

  return `${contextPrefix}my top pick is ${top.name} because it balances AI score, user rating, and real-world value ${detailParts.join(" ")}.`;
}

async function requestWithFallback<T>(request: () => Promise<T>, fallback: () => T | Promise<T>): Promise<T> {
  if (!IS_API_CONFIGURED) {
    return fallback();
  }

  try {
    return await request();
  } catch {
    return fallback();
  }
}

export async function askAssistant(message: string, sessionId?: string, limit = 4) {
  const safeLimit = Math.max(1, Math.min(8, Math.floor(limit)));
  const activeSessionId = sessionId ?? "local-session";

  return requestWithFallback(
    () =>
      apiRequest<AssistantMessageResponse>("/ai/assistant", {
        method: "POST",
        body: JSON.stringify({
          message,
          sessionId,
          limit: safeLimit,
        }),
      }).then((response) => ({
        ...response,
        workflow: normalizeWorkflow(response.workflow),
      })),
    () => {
      const previous = localConversations.get(activeSessionId);
      const baseWorkflow = localWorkflowFallback(message, safeLimit);
      const workflow = {
        ...baseWorkflow,
        intent: mergeIntent(baseWorkflow.intent, previous?.lastWorkflow?.intent ?? null),
      };

      const reply = buildHeuristicAssistantReply(message, workflow, previous?.lastWorkflow ?? null);

      localConversations.set(activeSessionId, {
        lastQuery: message,
        lastWorkflow: workflow,
      });

      return {
        sessionId: activeSessionId,
        reply,
        workflow,
      };
    }
  );
}

export async function getAIWorkflow(query: string, limit = 4) {
  const safeLimit = Math.max(1, Math.min(8, Math.floor(limit)));

  return requestWithFallback(
    () =>
      apiRequest<RecommendationWorkflow>(`/ai/recommendations${buildQueryString({ q: query, limit: safeLimit })}`).then(
        (workflow) => normalizeWorkflow(workflow)
      ),
    () => localWorkflowFallback(query, safeLimit)
  );
}

export async function getAIComparisonSummary(firstProductId: string, secondProductId: string) {
  return requestWithFallback(
    () =>
      apiRequest<ComparisonSummary>("/ai/compare-summary", {
        method: "POST",
        body: JSON.stringify({ firstProductId, secondProductId }),
      }),
    () => {
      const compared = resolveCompareProducts(firstProductId, secondProductId);
      return {
        winnerProductId: compared.firstProduct.aiScore >= compared.secondProduct.aiScore ? compared.firstProduct.id : compared.secondProduct.id,
        summary: `${compared.firstProduct.name} and ${compared.secondProduct.name} are close, but the winner edges ahead on overall AI score and user confidence for most buyers.`,
        keyAdvantages: [
          "Stronger combined AI score and user rating.",
          "Better day-to-day fit based on product strengths.",
        ],
        tradeOffs: [
          "The lower-priced option may offer better value for budget-focused buyers.",
          "Specs differ by workflow needs, so prioritize your primary use-case.",
        ],
      };
    }
  );
}

export async function getAIReviewSummary(productId: string) {
  return requestWithFallback(
    () => apiRequest<ReviewSummary>(`/ai/products/${productId}/review-summary`),
    () => {
      const product = products.find((item) => item.id === productId);
      if (!product) {
        return {
          positives: [],
          negatives: [],
          buyingAdvice: "Share your budget and priorities for a tailored recommendation.",
          finalVerdict: "I could not find this product right now, but I can suggest close alternatives.",
        };
      }

      return {
        positives: product.pros.slice(0, 3),
        negatives: product.cons.slice(0, 3),
        buyingAdvice: "Use this product if its top strengths match your daily use-case.",
        finalVerdict: product.reviewSummary,
      };
    }
  );
}

export async function getAIBuyingGuide(productId: string, alternativesLimit = 3) {
  const safeLimit = Math.max(1, Math.min(6, Math.floor(alternativesLimit)));

  return requestWithFallback(
    () =>
      apiRequest<BuyingGuide>(
        `/ai/products/${productId}/buying-guide${buildQueryString({ alternativesLimit: safeLimit })}`
      ).then((guide) => ({
        ...guide,
        alternatives: guide.alternatives.map((product) => normalizeProduct(product)),
      })),
    () => {
      const current = products.find((item) => item.id === productId);
      const alternatives = products.filter((item) => item.id !== productId).slice(0, safeLimit);

      return {
        worthBuying: Boolean(current && current.aiScore >= 85 && current.rating >= 4.1),
        verdict: current
          ? `${current.name} is a balanced option with strong day-to-day usability for the right buyer profile.`
          : "I can provide a buying guide once you pick a product.",
        bestFor: current?.bestFor.slice(0, 4) ?? [],
        alternatives,
        priceValueAnalysis: current
          ? `This product sits in a competitive price band. Compare features against similarly priced alternatives before buying.`
          : "Price-value analysis is available once a product is selected.",
      };
    }
  );
}
