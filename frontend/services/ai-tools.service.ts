import { apiRequest, buildQueryString, withApiFallback } from "@/services/api";
import type { AITool, AIToolCompareResponse, AIToolsCatalogResponse, AIToolSearchResponse } from "@/types/ai-tools";

function toNumber(value: unknown): number | null {
  if (value === null || value === undefined) {
    return null;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return null;
}

function normalizeAITool(tool: AITool): AITool {
  return {
    ...tool,
    letrustoScore: toNumber(tool.letrustoScore),
    pricing: {
      ...tool.pricing,
      amount: toNumber(tool.pricing.amount),
    },
  };
}

export async function getAiTools() {
  return withApiFallback(
    () => apiRequest<AIToolsCatalogResponse>("/ai-tools").then((response) => ({
      items: response.items.map(normalizeAITool),
    })),
    () => ({ items: [] })
  );
}

export async function getAiToolBySlug(slug: string) {
  return withApiFallback(
    () => apiRequest<AITool>(`/ai-tools/${slug}`).then((tool) => normalizeAITool(tool)),
    () => null
  );
}

export async function searchAiTools(options: {
  q?: string;
  category?: string;
  pricingModel?: string;
  platform?: string;
  integration?: string;
  tag?: string;
  page?: number;
  pageSize?: number;
}) {
  return withApiFallback(
    () =>
      apiRequest<AIToolSearchResponse>(
        `/ai-tools/search${buildQueryString({
          q: options.q,
          category: options.category,
          pricingModel: options.pricingModel,
          platform: options.platform,
          integration: options.integration,
          tag: options.tag,
          page: options.page,
          pageSize: options.pageSize,
        })}`
      ).then((response) => ({
        ...response,
        items: response.items.map(normalizeAITool),
      })),
    () => ({
      items: [],
      pagination: {
        page: 1,
        pageSize: options.pageSize ?? 12,
        totalItems: 0,
        totalPages: 1,
        hasNextPage: false,
        hasPreviousPage: false,
      },
    })
  );
}

export async function compareAiTools(first?: string, second?: string) {
  return withApiFallback(
    () =>
      apiRequest<AIToolCompareResponse>(
        `/ai-tools/compare${buildQueryString({ first, second })}`
      ).then((response) => ({
        firstTool: normalizeAITool(response.firstTool),
        secondTool: normalizeAITool(response.secondTool),
      })),
    () => null
  );
}
