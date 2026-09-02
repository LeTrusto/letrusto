export type DigitalProductStatus = "draft" | "published" | "archived";

export type DigitalProductCategory = {
  slug: string;
  name: string;
  description: string;
};

export type DigitalProduct = {
  id: string;
  name: string;
  slug: string;
  description: string;
  valueProposition: string;
  category: DigitalProductCategory;
  format: string;
  price: number;
  currency: "INR";
  previewLabel: string;
  included: string[];
  audience: string[];
  usage: string[];
  status: DigitalProductStatus;
  delivery: "protected-download";
  assetVersion: string;
  faq: Array<{ question: string; answer: string }>;
};