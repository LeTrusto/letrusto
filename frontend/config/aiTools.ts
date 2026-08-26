export type AIToolsCategory = {
  id: string;
  name: string;
  description: string;
  href: string;
  icon: string;
  artworkKey: string;
  eyebrow: string;
  featuredBullets: string[];
  categoryHints: string[];
};

export type AICategoryArtwork = {
  src: string;
  fit: "object-cover" | "object-contain";
  position: string;
  frameInset: string;
  panelBackground: string;
};

// Legacy AI tools categories — no longer used in the POD direction.
export const AI_TOOLS_PUBLIC_CATEGORIES: AIToolsCategory[] = [];

export const AI_CATEGORY_ARTWORK: Record<string, AICategoryArtwork> = {};

export const DEPRECATED_PUBLIC_CATEGORIES: string[] = [];
