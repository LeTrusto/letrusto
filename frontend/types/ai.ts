import type { Product } from "@/types/products";

export type ShoppingIntent = {
  budgetMin: number | null;
  budgetMax: number | null;
  usage: string | null;
  category: string | null;
  priorities: string[];
};

export type RankedRecommendation = {
  product: Product;
  score: number;
  reasons: string[];
};

export type RecommendationWorkflow = {
  intent: ShoppingIntent;
  explanation: string;
  rankedRecommendations: RankedRecommendation[];
  followUpQuestions: string[];
};

export type AssistantMessageResponse = {
  sessionId: string;
  reply: string;
  workflow: RecommendationWorkflow;
};

export type ComparisonSummary = {
  winnerProductId: string;
  summary: string;
  keyAdvantages: string[];
  tradeOffs: string[];
};

export type ReviewSummary = {
  positives: string[];
  negatives: string[];
  buyingAdvice: string;
  finalVerdict: string;
};

export type BuyingGuide = {
  worthBuying: boolean;
  verdict: string;
  bestFor: string[];
  alternatives: Product[];
  priceValueAnalysis: string;
};
