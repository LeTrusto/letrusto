export type AIToolsCategory = {
  id: string;
  name: string;
  description: string;
  href: string;
  icon: string;
  eyebrow: string;
  featuredBullets: string[];
  categoryHints: string[];
};

// Stage 1 public categories for the AI Tools and Software direction.
export const AI_TOOLS_PUBLIC_CATEGORIES: AIToolsCategory[] = [
  {
    id: "ai-assistants",
    name: "AI Assistants",
    description: "General-purpose AI assistants for planning, analysis, and daily decision support.",
    href: "/category/ai-assistants",
    icon: "🤖",
    eyebrow: "Priority",
    featuredBullets: ["Research", "Daily workflows", "Q&A", "Task planning"],
    categoryHints: ["assistant", "chat", "copilot", "ai assistant"],
  },
  {
    id: "ai-writing",
    name: "AI Writing",
    description: "Tools for drafting, rewriting, editing, and content operations across teams.",
    href: "/category/ai-writing",
    icon: "✍️",
    eyebrow: "Priority",
    featuredBullets: ["Drafting", "Editing", "SEO writing", "Repurposing"],
    categoryHints: ["writing", "copy", "content", "editor"],
  },
  {
    id: "ai-image-design",
    name: "AI Image & Design",
    description: "Visual generation and design tools for marketing, product, and creative teams.",
    href: "/category/ai-image-design",
    icon: "🎨",
    eyebrow: "Priority",
    featuredBullets: ["Image generation", "Brand assets", "Mockups", "Creative workflows"],
    categoryHints: ["image", "design", "graphics", "creative"],
  },
  {
    id: "ai-video-audio",
    name: "AI Video & Audio",
    description: "AI tools for video production, voice workflows, and media enhancement.",
    href: "/category/ai-video-audio",
    icon: "🎬",
    eyebrow: "Priority",
    featuredBullets: ["Video creation", "Voice tools", "Editing", "Repurposing"],
    categoryHints: ["video", "audio", "voice", "podcast"],
  },
  {
    id: "ai-coding-developer-tools",
    name: "AI Coding & Developer Tools",
    description: "Developer-first AI tools for coding, debugging, documentation, and shipping faster.",
    href: "/category/ai-coding-developer-tools",
    icon: "💻",
    eyebrow: "Priority",
    featuredBullets: ["Code generation", "Debugging", "Documentation", "Code review"],
    categoryHints: ["coding", "developer", "devtool", "programming"],
  },
];

// Publicly deprecated in Stage 1 (hidden from primary homepage/navigation surfaces).
export const DEPRECATED_PUBLIC_CATEGORIES: string[] = [
  "electronics",
  "beauty",
  "pet-care",
  "home-kitchen",
  "kitchen",
  "fitness",
  "travel",
  "finance",
  "insurance",
];
