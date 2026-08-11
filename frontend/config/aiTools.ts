export type AIToolsCategory = {
  id: string;
  name: string;
  description: string;
  href: string;
  icon: string;
  artworkKey:
    | "assistant-workspace"
    | "writing-studio"
    | "image-design-canvas"
    | "video-audio-timeline"
    | "coding-dev-workflow"
    | "marketing-automation";
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

// Stage 1 public categories for the AI Tools and Software direction.
export const AI_TOOLS_PUBLIC_CATEGORIES: AIToolsCategory[] = [
  {
    id: "ai-assistants",
    name: "AI Assistants",
    description: "General-purpose AI assistants for planning, analysis, and daily decision support.",
    href: "/category/ai-assistants",
    icon: "🤖",
    artworkKey: "assistant-workspace",
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
    artworkKey: "writing-studio",
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
    artworkKey: "image-design-canvas",
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
    artworkKey: "video-audio-timeline",
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
    artworkKey: "coding-dev-workflow",
    eyebrow: "Priority",
    featuredBullets: ["Code generation", "Debugging", "Documentation", "Code review"],
    categoryHints: ["coding", "developer", "devtool", "programming"],
  },
  {
    id: "marketing-automation",
    name: "Marketing & Automation",
    description: "All-in-one CRM, marketing automation, and lead management platforms for agencies and businesses.",
    href: "/category/marketing-automation",
    icon: "📈",
    artworkKey: "marketing-automation",
    eyebrow: "New",
    featuredBullets: ["CRM", "Email marketing", "Funnels", "Automation"],
    categoryHints: ["marketing", "crm", "automation", "lead generation", "agency", "funnel"],
  },
];

export const AI_CATEGORY_ARTWORK: Record<AIToolsCategory["artworkKey"], AICategoryArtwork> = {
  "assistant-workspace": {
    src: "/images/categories/ai-assistants.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-4",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(236,253,255,0.96),_rgba(224,242,254,0.93))]",
  },
  "writing-studio": {
    src: "/images/categories/ai-writing.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-4",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(255,247,237,0.97),_rgba(254,242,242,0.93))]",
  },
  "image-design-canvas": {
    src: "/images/categories/ai-image-design.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-3",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(245,243,255,0.96),_rgba(238,242,255,0.93))]",
  },
  "video-audio-timeline": {
    src: "/images/categories/ai-video-audio.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-3",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(240,249,255,0.96),_rgba(224,231,255,0.93))]",
  },
  "coding-dev-workflow": {
    src: "/images/categories/ai-coding-developer-tools.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-3",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(241,245,249,0.97),_rgba(224,242,254,0.93))]",
  },
  "marketing-automation": {
    src: "/images/categories/ai-assistants.svg",
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-4",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(252,231,243,0.96),_rgba(245,243,255,0.93))]",
  },
};

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
