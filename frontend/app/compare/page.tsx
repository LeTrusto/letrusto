import type { Metadata } from "next";
import Script from "next/script";
import Link from "next/link";
import { ArrowUpRight, Crown } from "lucide-react";

import SchemaOrg from "@/components/SchemaOrg";
import { compareAiTools, getAiTools } from "@/services/ai-tools.service";
import { getSearchParamValue } from "@/utils/helpers";

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

function joinOrFallback(items: string[], fallback = "Not publicly listed") {
  return items.length > 0 ? items.join(", ") : fallback;
}

function toolScore(tool: {
  letrustoScore: number | null;
  pros: string[];
  features: string[];
  integrations: string[];
}) {
  return (
    (tool.letrustoScore ?? 0) +
    tool.pros.length * 1.8 +
    tool.features.length * 1.2 +
    tool.integrations.length * 0.6
  );
}

export const metadata: Metadata = {
  title: "AI Tool Comparison",
  description: "Compare two tools side by side with AI analysis, key strengths, and value insights.",
  alternates: {
    canonical: "/compare",
  },
  openGraph: {
    title: "AI Tool Comparison",
    description: "Compare two tools side by side with AI analysis, key strengths, and value insights.",
    url: "/compare",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Tool Comparison",
    description: "Compare two tools side by side with AI analysis, key strengths, and value insights.",
    images: ["/images/og-default.svg"],
  },
};

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<{ first?: string | string[]; second?: string | string[] }>;
}) {
  const params = await searchParams;
  const catalogResponse = await getAiTools();
  const catalog = catalogResponse.items;

  if (catalog.length === 0) {
    return (
      <main className="min-h-screen bg-slate-50 px-6 py-14">
        <div className="mx-auto max-w-5xl rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <h1 className="text-3xl font-black text-slate-900">AI Tool Comparison</h1>
          <p className="mt-3 text-slate-600">No published AI tools are available for comparison yet.</p>
          <Link href="/ai-tools" className="mt-6 inline-flex rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800">
            Browse AI Tools
          </Link>
        </div>
      </main>
    );
  }

  const requestedFirst = getSearchParamValue(params.first);
  const requestedSecond = getSearchParamValue(params.second);

  const firstSlug = catalog.some((tool) => tool.slug === requestedFirst) ? requestedFirst : catalog[0].slug;
  const secondFallback = catalog.find((tool) => tool.slug !== firstSlug)?.slug ?? firstSlug;
  const secondSlug = catalog.some((tool) => tool.slug === requestedSecond && tool.slug !== firstSlug)
    ? requestedSecond
    : secondFallback;

  const compared = await compareAiTools(firstSlug, secondSlug);
  const firstTool = compared?.firstTool ?? catalog.find((tool) => tool.slug === firstSlug) ?? catalog[0];
  const secondTool = compared?.secondTool ?? catalog.find((tool) => tool.slug === secondSlug) ?? catalog[0];
  const winner = toolScore(firstTool) >= toolScore(secondTool) ? firstTool : secondTool;

  const comparisonRows = [
    {
      label: "Provider",
      first: firstTool.provider,
      second: secondTool.provider,
    },
    {
      label: "Category",
      first: firstTool.category.name,
      second: secondTool.category.name,
    },
    {
      label: "Best For",
      first: joinOrFallback(firstTool.bestFor),
      second: joinOrFallback(secondTool.bestFor),
    },
    {
      label: "Pricing",
      first: formatPricing(firstTool.pricing),
      second: formatPricing(secondTool.pricing),
    },
    {
      label: "Platforms",
      first: joinOrFallback(firstTool.platforms),
      second: joinOrFallback(secondTool.platforms),
    },
    {
      label: "Integrations",
      first: joinOrFallback(firstTool.integrations),
      second: joinOrFallback(secondTool.integrations),
    },
    {
      label: "Features",
      first: joinOrFallback(firstTool.features),
      second: joinOrFallback(secondTool.features),
    },
    {
      label: "Pros",
      first: joinOrFallback(firstTool.pros),
      second: joinOrFallback(secondTool.pros),
    },
    {
      label: "Cons",
      first: joinOrFallback(firstTool.cons),
      second: joinOrFallback(secondTool.cons),
    },
    {
      label: "LeTrusto Score",
      first: firstTool.letrustoScore !== null ? String(firstTool.letrustoScore) : "Not available",
      second: secondTool.letrustoScore !== null ? String(secondTool.letrustoScore) : "Not available",
    },
    {
      label: "Pricing Verification",
      first: toDateLabel(firstTool.lastVerifiedAt),
      second: toDateLabel(secondTool.lastVerifiedAt),
    },
  ];

  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://letrusto.com" },
      { "@type": "ListItem", position: 2, name: "Compare", item: "https://letrusto.com/compare" },
    ],
  };

  return (
    <main className="min-h-screen bg-slate-50 p-10">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "AI Tool Comparison",
          url: "https://letrusto.com/compare",
          description: "Compare published AI tools side by side with category fit, pricing, features, and platform support.",
        }}
      />
      <Script id="compare-breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-black text-center mb-3 text-slate-950">AI Tool Comparison</h1>

        <p className="text-center text-slate-500 mb-12">
          Compare published AI tools using real category fit, pricing context, and documented strengths.
        </p>

        <form className="mb-10 grid gap-4 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-3" method="get">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="first">
              First Tool
            </label>
            <select id="first" name="first" defaultValue={firstTool.slug} className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-sky-500">
              {catalog.map((tool) => (
                <option key={tool.slug} value={tool.slug}>
                  {tool.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="second">
              Second Tool
            </label>
            <select id="second" name="second" defaultValue={secondTool.slug} className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-sky-500">
              {catalog.map((tool) => (
                <option key={tool.slug} value={tool.slug}>
                  {tool.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button className="w-full rounded-2xl bg-gradient-to-r from-cyan-600 to-sky-600 px-6 py-3 font-semibold text-white transition hover:from-cyan-700 hover:to-sky-700" type="submit">
              Compare Now
            </button>
          </div>
        </form>

        <div className="grid md:grid-cols-2 gap-6">
          {[firstTool, secondTool].map((tool) => {
            const isWinner = winner.slug === tool.slug;
            return (
            <div
              key={tool.slug}
              className={`relative rounded-2xl border-2 bg-white p-6 shadow-sm transition ${isWinner ? "border-emerald-400 shadow-emerald-100" : "border-slate-200"}`}
            >
              {isWinner && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="flex items-center gap-1.5 rounded-full bg-emerald-500 px-4 py-1 text-sm font-bold text-white shadow-lg">
                    <Crown className="h-4 w-4" /> Best Overall
                  </span>
                </div>
              )}
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{tool.category.name}</p>
              <h2 className="mt-2 text-center text-2xl font-black text-slate-900">{tool.name}</h2>
              <p className="text-center text-sm text-slate-500">{tool.provider}</p>
              <p className="mt-3 text-sm text-slate-600 text-center">{tool.description}</p>

              <div className="mt-4 grid grid-cols-2 gap-2 text-center">
                <div className="rounded-xl bg-sky-50 px-2 py-2">
                  <div className="text-xs font-semibold text-sky-700">Category</div>
                  <div className="text-sm font-bold text-sky-900">{tool.category.name}</div>
                </div>
                <div className="rounded-xl bg-indigo-50 px-2 py-2">
                  <div className="text-xs font-semibold text-indigo-700">LeTrusto Score</div>
                  <div className="text-sm font-bold text-indigo-900">{tool.letrustoScore ?? "N/A"}</div>
                </div>
              </div>

              <ul className="mt-4 space-y-1.5">
                {tool.features.slice(0, 4).map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-slate-600">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs text-sky-700">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <Link href={`/ai-tools/${tool.slug}`} className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-900 hover:text-sky-700">
                Open profile
                <ArrowUpRight className="h-4 w-4" />
              </Link>
            </div>
            );
          })}

        </div>

        <div className="mt-12 overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-lg shadow-slate-200/60">
          <div className="border-b border-slate-100 px-6 py-5">
            <h2 className="text-2xl font-bold text-slate-900">AI Tool Comparison Matrix</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left">
              <thead className="sticky top-24 z-10 bg-slate-50 text-sm uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-6 py-4">Field</th>
                  <th className="px-6 py-4">{firstTool.name}</th>
                  <th className="px-6 py-4">{secondTool.name}</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map((row) => (
                  <tr key={row.label} className="border-t border-slate-100">
                    <td className="px-6 py-4 font-semibold text-slate-700">{row.label}</td>
                    <td className="px-6 py-4 text-slate-700">{row.first}</td>
                    <td className="px-6 py-4 text-slate-700">{row.second}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-sky-50 border border-sky-200 rounded-2xl mt-12 p-8">
          <h2 className="text-2xl font-bold text-sky-800 mb-4">
            🤖 LeTrusto AI Verdict
          </h2>

          <p className="text-lg">
            <b>Winner: {winner.name}</b>
          </p>

          <p className="mt-3 text-slate-700">
            This verdict prioritizes documented category fit, practical features, platform support, and known tool strengths.
          </p>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Why It Leads</p>
              <ul className="mt-2 space-y-2 text-slate-700">
                {winner.pros.slice(0, 3).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Trade-offs</p>
              <ul className="mt-2 space-y-2 text-slate-700">
                {winner.cons.slice(0, 3).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </div>
          </div>

        </div>

      </div>
    </main>
  );
}