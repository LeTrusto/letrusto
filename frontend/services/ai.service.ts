import { apiRequest, buildQueryString } from "@/services/api";
import type {
  AssistantMessageResponse,
  BuyingGuide,
  ComparisonSummary,
  RecommendationWorkflow,
  ReviewSummary,
} from "@/types/ai";
import type { Product } from "@/types/products";

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

export async function askAssistant(message: string, sessionId?: string, limit = 4) {
  const safeLimit = Math.max(1, Math.min(8, Math.floor(limit)));

  return apiRequest<AssistantMessageResponse>("/ai/assistant", {
        method: "POST",
        body: JSON.stringify({
          message,
          sessionId,
          limit: safeLimit,
        }),
      }).then((response) => ({ ...response, workflow: normalizeWorkflow(response.workflow) }));
}

export async function getAIWorkflow(query: string, limit = 4) {
  const safeLimit = Math.max(1, Math.min(8, Math.floor(limit)));

  return apiRequest<RecommendationWorkflow>(`/ai/recommendations${buildQueryString({ q: query, limit: safeLimit })}`).then(
    (workflow) => normalizeWorkflow(workflow)
  );
}

export async function getAIComparisonSummary(firstProductId: string, secondProductId: string) {
  return apiRequest<ComparisonSummary>("/ai/compare-summary", {
        method: "POST",
        body: JSON.stringify({ firstProductId, secondProductId }),
      });
}

export async function getAIReviewSummary(productId: string) {
  return apiRequest<ReviewSummary>(`/ai/products/${productId}/review-summary`);
}

export async function getAIBuyingGuide(productId: string, alternativesLimit = 3) {
  const safeLimit = Math.max(1, Math.min(6, Math.floor(alternativesLimit)));

  return apiRequest<BuyingGuide>(
        `/ai/products/${productId}/buying-guide${buildQueryString({ alternativesLimit: safeLimit })}`
      ).then((guide) => ({
        ...guide,
        alternatives: guide.alternatives.map((product) => normalizeProduct(product)),
      }));
}
