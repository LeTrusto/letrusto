export type AIToolLifecycleStatus = "draft" | "published" | "archived";

export type AIToolPricingModel = "free" | "free_trial" | "monthly" | "yearly" | "custom";

export type AIToolCategory = {
  id: number;
  name: string;
  slug: string;
  position: number;
};

export type AIToolPricing = {
  model: AIToolPricingModel | null;
  amount: number | null;
  currency: string | null;
  period: string | null;
  hasFreePlan: boolean | null;
  hasFreeTrial: boolean | null;
  trialDays: number | null;
  notes: string | null;
  pricingUrl: string | null;
};

export type AITool = {
  id: string;
  slug: string;
  name: string;
  provider: string;
  description: string;
  websiteUrl: string;
  logoUrl: string | null;
  category: AIToolCategory;
  lifecycleStatus: AIToolLifecycleStatus;
  pricing: AIToolPricing;
  letrustoScore: number | null;
  useCases: string[];
  features: string[];
  pros: string[];
  cons: string[];
  bestFor: string[];
  notIdealFor: string[];
  whyLetrustoRecommends: string | null;
  tags: string[];
  platforms: string[];
  integrations: string[];
  affiliateAvailable: boolean;
  affiliateUrl: string | null;
  lastVerifiedAt: string | null;
};

export type AIToolsCatalogResponse = {
  items: AITool[];
};

export type AIToolPagination = {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
};

export type AIToolSearchResponse = {
  items: AITool[];
  pagination: AIToolPagination;
};

export type AIToolCompareResponse = {
  firstTool: AITool;
  secondTool: AITool;
};

export type AIToolRecommendationCandidateResponse = {
  items: AITool[];
  note: string;
};
