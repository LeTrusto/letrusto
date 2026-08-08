import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

import ProductCard from "@/components/ProductCard";
import SchemaOrg from "@/components/SchemaOrg";
import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";
import { CATALOG_TREE, getCategoryLabel } from "@/constants/index";
import { getAiTools } from "@/services/ai-tools.service";
import { getCatalogMetadata, getProductSearch } from "@/services/product.service";

type Props = { params: Promise<{ slug: string }> };

type ComingSoonProfile = {
  illustration: string;
  description: string;
  expected: string[];
};

const COMING_SOON_PROFILES: Record<string, ComingSoonProfile> = {
  "ai-assistants": {
    illustration: "ASSIST",
    description: "We are curating trusted AI assistant recommendations for work, research, and team decision support.",
    expected: ["General assistants", "Reasoning quality", "Team workflows", "Security and trust"],
  },
  "ai-writing": {
    illustration: "WRITE",
    description: "We are curating AI writing tools for drafting, editing, SEO workflows, and content operations.",
    expected: ["Drafting", "Editing and tone", "SEO workflows", "Team collaboration"],
  },
  "ai-image-design": {
    illustration: "DESIGN",
    description: "We are curating AI image and design tools for marketing, product, and creative teams.",
    expected: ["Image generation", "Brand assets", "Mockups", "Creative speed"],
  },
  "ai-video-audio": {
    illustration: "MEDIA",
    description: "We are curating AI video and audio tools for creators and media teams.",
    expected: ["Video editing", "Voice generation", "Repurposing", "Production quality"],
  },
  "ai-coding-developer-tools": {
    illustration: "DEV",
    description: "We are curating AI coding and developer tools for faster shipping and higher code quality.",
    expected: ["Code generation", "Debugging", "Code review", "Developer workflows"],
  },
  hosting: {
    illustration: "HOST",
    description: "We're curating trusted hosting recommendations for software teams and creators.",
    expected: ["Hostinger", "Cloudways", "Namecheap", "Google Workspace", "Website Builders", "AI Tools"],
  },
  saas: {
    illustration: "SAAS",
    description: "We're curating trusted SaaS recommendations for business workflows and growth teams.",
    expected: ["CRM", "Project Management", "Automation", "Knowledge Base", "Collaboration", "Analytics"],
  },
  beauty: {
    illustration: "BEAUTY",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Skincare", "Hair Care", "Wellness", "Cosmetics"],
  },
  "pet-care": {
    illustration: "PET",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Food", "Health", "Accessories", "Training"],
  },
  kitchen: {
    illustration: "KITCHEN",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Cookware", "Mixers", "Air Fryers", "Water Purifiers"],
  },
  fitness: {
    illustration: "FIT",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Wearables", "Recovery", "Training Gear", "Nutrition Tools"],
  },
  "home-kitchen": {
    illustration: "HOME",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Appliances", "Cleaning", "Smart Home", "Organization"],
  },
  travel: {
    illustration: "TRAVEL",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Luggage", "Travel Cards", "Connectivity", "Safety Essentials"],
  },
  finance: {
    illustration: "FIN",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Credit Cards", "Savings Tools", "Budgeting Apps", "Investment Platforms"],
  },
  insurance: {
    illustration: "SAFE",
    description: "We're carefully curating the best products and recommendations for this category.",
    expected: ["Health Insurance", "Term Plans", "Vehicle Cover", "Travel Cover"],
  },
};

function resolveComingSoonProfile(slug: string): ComingSoonProfile {
  return (
    COMING_SOON_PROFILES[slug] ?? {
      illustration: "SOON",
      description: "We're curating trusted AI tools and software recommendations for this category.",
      expected: ["Top tools", "Trusted reviews", "Comparisons", "Buying guides"],
    }
  );
}

function isAiCategorySlug(slug: string) {
  return AI_TOOLS_PUBLIC_CATEGORIES.some((category) => category.id === slug);
}

function toDateLabel(value: string | null) {
  if (!value) {
    return "Not available";
  }

  return new Date(value).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatPricing(toolPricing: {
  model: string | null;
  amount: number | null;
  currency: string | null;
  period: string | null;
  notes: string | null;
}) {
  if (!toolPricing.model) {
    return "Not publicly verified";
  }

  if (toolPricing.amount !== null && toolPricing.currency && toolPricing.period) {
    return `${toolPricing.currency} ${toolPricing.amount} / ${toolPricing.period}`;
  }

  return toolPricing.notes || toolPricing.model.replace("_", " ");
}

function CategoryBreadcrumbSchema({ slug, label }: { slug: string; label: string }) {
  return (
    <Script
      id={`category-breadcrumb-${slug}`}
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: [
            { "@type": "ListItem", position: 1, name: "Home", item: "https://letrusto.com" },
            { "@type": "ListItem", position: 2, name: "Categories", item: "https://letrusto.com/categories" },
            { "@type": "ListItem", position: 3, name: label, item: `https://letrusto.com/category/${slug}` },
          ],
        }),
      }}
    />
  );
}

function ComingSoonCategory({ slug, label }: { slug: string; label: string }) {
  const profile = resolveComingSoonProfile(slug);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-orange-50">
      <SchemaOrg
        type="WebPage"
        data={{
          name: `${label} AI Tools`,
          url: `https://letrusto.com/category/${slug}`,
          description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
        }}
      />
      <CategoryBreadcrumbSchema slug={slug} label={label} />
      <section className="mx-auto max-w-6xl px-6 py-16 md:py-20">
        <article className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm md:p-12">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" aria-hidden="true" />

          <div className="relative z-10 grid gap-8 lg:grid-cols-[1.1fr_1fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Coming Soon</p>
              <div className="mt-4 inline-flex rounded-2xl border border-violet-200 bg-violet-50 px-4 py-2 text-sm font-black tracking-[0.16em] text-violet-700">
                {profile.illustration}
              </div>
              <h1 className="mt-4 text-4xl font-black tracking-tight text-slate-900 md:text-5xl">{label}</h1>
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-600 md:text-base">{profile.description}</p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href="/support?tab=contact&category=feedback"
                  className="rounded-xl bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 px-5 py-3 text-sm font-bold text-white"
                >
                  Notify Me
                </Link>
                <Link
                  href="/"
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
                >
                  Return Home
                </Link>
                <Link
                  href="/ai"
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
                >
                  Ask LeTrusto
                </Link>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 md:p-7">
              <svg viewBox="0 0 360 150" className="mb-5 h-[120px] w-full text-violet-700/45" aria-hidden="true">
                <defs>
                  <linearGradient id="coming-soon-line" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="currentColor" stopOpacity="0.75" />
                    <stop offset="100%" stopColor="currentColor" stopOpacity="0.2" />
                  </linearGradient>
                </defs>
                <rect x="16" y="16" width="328" height="118" rx="22" fill="none" stroke="url(#coming-soon-line)" strokeWidth="2" />
                <path d="M40 102c28-34 55-52 93-52 40 0 58 20 91 20 28 0 47-11 91-39" fill="none" stroke="url(#coming-soon-line)" strokeWidth="8" strokeLinecap="round" />
                <circle cx="268" cy="60" r="22" fill="none" stroke="url(#coming-soon-line)" strokeWidth="2" />
                <rect x="80" y="56" width="80" height="34" rx="12" fill="none" stroke="url(#coming-soon-line)" strokeWidth="2" />
              </svg>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">What you can expect</p>
              <ul className="mt-4 space-y-2.5 text-sm text-slate-700 md:text-base">
                {profile.expected.map((entry) => (
                  <li key={`${slug}-${entry}`} className="flex items-start gap-2.5">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-fuchsia-600" />
                    <span>{entry}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </article>
      </section>
    </main>
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const label = getCategoryLabel(slug);
  return {
    title: `${label} AI Tools`,
    description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
    alternates: {
      canonical: `/category/${slug}`,
    },
    openGraph: {
      title: `${label} AI Tools`,
      description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
      url: `/category/${slug}`,
      siteName: "LeTrusto",
      type: "website",
      images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      title: `${label} AI Tools`,
      description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
      images: ["/images/og-default.svg"],
    },
  };
}

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;
  const label = getCategoryLabel(slug);

  if (isAiCategorySlug(slug)) {
    const toolsResponse = await getAiTools();
    const tools = toolsResponse.items.filter((tool) => tool.category.slug === slug);

    if (tools.length === 0) {
      return <ComingSoonCategory slug={slug} label={label} />;
    }

    return (
      <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(125,211,252,0.11),_transparent_24%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
        <SchemaOrg
          type="WebPage"
          data={{
            name: `${label} AI Tools`,
            url: `https://letrusto.com/category/${slug}`,
            description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
          }}
        />
        <CategoryBreadcrumbSchema slug={slug} label={label} />

        <section className="mx-auto max-w-7xl px-6 py-14 md:py-18">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">AI Category</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-5xl">{label}</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Compare published AI tools in this category with transparent details for pricing, strengths, and integrations.
          </p>

          <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {tools.map((tool) => (
              <article key={tool.slug} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{tool.category.name}</p>
                <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">{tool.name}</h2>
                <p className="text-sm font-semibold text-slate-600">{tool.provider}</p>
                <p className="mt-3 text-sm leading-relaxed text-slate-600">{tool.description}</p>

                <div className="mt-4 space-y-1.5 text-sm text-slate-700">
                  <p><span className="font-semibold">Best for:</span> {tool.bestFor.length > 0 ? tool.bestFor.join(", ") : "Not publicly listed"}</p>
                  <p><span className="font-semibold">Pricing:</span> {formatPricing(tool.pricing)}</p>
                  <p><span className="font-semibold">Platforms:</span> {tool.platforms.length > 0 ? tool.platforms.join(", ") : "Not publicly listed"}</p>
                  <p><span className="font-semibold">Integrations:</span> {tool.integrations.length > 0 ? tool.integrations.join(", ") : "Not publicly listed"}</p>
                  <p><span className="font-semibold">Last verified:</span> {toDateLabel(tool.lastVerifiedAt)}</p>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Link href={`/ai-tools/${tool.slug}`} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">
                    View profile
                  </Link>
                  <Link href={`/compare?first=${tool.slug}`} className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:border-slate-500">
                    Compare
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    );
  }

  const [searchResult, metadata] = await Promise.all([
    getProductSearch({ category: slug, pageSize: 24, sortBy: "ai-high" }),
    getCatalogMetadata(),
  ]);

  const products = searchResult.items;

  if (products.length === 0) {
    return <ComingSoonCategory slug={slug} label={label} />;
  }

  const parent = CATALOG_TREE.find((node) => node.children?.some((child) => child.slug === slug));
  const siblingCategories = parent?.children?.filter((child) => child.slug !== slug).slice(0, 5) ?? [];

  return (
    <main className="min-h-screen bg-white">
      <SchemaOrg
        type="WebPage"
        data={{
          name: `${label} AI Tools`,
          url: `https://letrusto.com/category/${slug}`,
          description: `Explore ${label} tools, comparisons, and buying guidance on LeTrusto.`,
        }}
      />
      <CategoryBreadcrumbSchema slug={slug} label={label} />
      <section className="bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 py-14 text-white">
        <div className="mx-auto max-w-7xl px-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-white/70">AI Category Hub</p>
          <h1 className="mt-3 text-3xl font-black tracking-tight md:text-5xl">{label}</h1>
          <p className="mt-4 max-w-2xl text-white/90 md:text-lg">
            LeTrusto ranks tools by practical value, trust indicators, and real-world workflow fit.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href={`/ai?q=Best ${label}`} className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-violet-700">
              Get recommendations for {label}
            </Link>
            <Link href={`/search?category=${slug}`} className="rounded-xl border border-white/40 px-5 py-2.5 text-sm font-semibold text-white">
              Advanced filters
            </Link>
          </div>
        </div>
      </section>

      {siblingCategories.length > 0 ? (
        <section className="border-b border-slate-100 bg-slate-50">
          <div className="mx-auto flex max-w-7xl gap-2 overflow-x-auto px-6 py-3">
            {siblingCategories.map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="shrink-0 rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-semibold text-slate-600 hover:border-violet-300 hover:text-violet-700">
                {cat.name}
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-black tracking-tight text-slate-900">{searchResult.pagination.totalItems} AI-ranked options</h2>
            <p className="mt-1 text-sm text-slate-500">We prioritize recommendation quality over catalog density.</p>
          </div>
          <Link href={`/search?category=${slug}`} className="text-sm font-semibold text-violet-700 hover:underline">
            View full search
          </Link>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product, index) => (
            <ProductCard
              key={product.id}
              product={product}
              priority={index < 4}
              highlightLabel={metadata.productSpotlightBadges[product.id] ?? "AI Ranked"}
              aiHighlights={product.pros.slice(0, 3)}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
