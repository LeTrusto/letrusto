export type ServiceStatus = "published" | "draft" | "archived";

export type ServicePricing = {
  model: "custom-quote" | "starting-from" | "fixed-package";
  startingPrice?: number;
  notes: string;
};

export type Service = {
  id: string;
  name: string;
  slug: string;
  category: string;
  description: string;
  useCase: string;
  problem: string;
  included: string[];
  exclusions: string[];
  process: string[];
  informationNeeded: string[];
  status: ServiceStatus;
  pricing: ServicePricing;
  seo: { title: string; description: string };
};