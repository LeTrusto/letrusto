import type { Metadata } from "next";
import Image from "next/image";
import Script from "next/script";
import { Crown, TrendingDown } from "lucide-react";

import SchemaOrg from "@/components/SchemaOrg";
import { getAIComparisonSummary } from "@/services/ai.service";
import { getAllProducts, getCompareProducts } from "@/services/product.service";
import { getSearchParamValue } from "@/utils/helpers";

export const metadata: Metadata = {
  title: "Product Comparison",
  description: "Compare two products side by side with AI analysis, key specs, and value insights.",
  alternates: {
    canonical: "/compare",
  },
  openGraph: {
    title: "Product Comparison",
    description: "Compare two products side by side with AI analysis, key specs, and value insights.",
    url: "/compare",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Product Comparison",
    description: "Compare two products side by side with AI analysis, key specs, and value insights.",
    images: ["/images/og-default.svg"],
  },
};

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<{ first?: string | string[]; second?: string | string[] }>;
}) {
  const params = await searchParams;
  const [catalog, compared] = await Promise.all([
    getAllProducts(),
    getCompareProducts(getSearchParamValue(params.first), getSearchParamValue(params.second)),
  ]);
  const { firstProduct, secondProduct } = compared;

  const specLabels = Array.from(
    new Set([
      ...firstProduct.specs.map((spec) => spec.label),
      ...secondProduct.specs.map((spec) => spec.label),
    ])
  );

  const firstSpecs = new Map(firstProduct.specs.map((spec) => [spec.label, spec.value]));
  const secondSpecs = new Map(secondProduct.specs.map((spec) => [spec.label, spec.value]));
  const firstScore = firstProduct.aiScore + firstProduct.rating * 10 + firstProduct.pros.length;
  const secondScore = secondProduct.aiScore + secondProduct.rating * 10 + secondProduct.pros.length;
  const winner = firstScore >= secondScore ? firstProduct : secondProduct;
  const valueWinner = firstProduct.priceValue <= secondProduct.priceValue ? firstProduct : secondProduct;
  const aiSummary = await getAIComparisonSummary(firstProduct.id, secondProduct.id);
  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://letrusto.com" },
      { "@type": "ListItem", position: 2, name: "Compare", item: "https://letrusto.com/compare" },
    ],
  };

  return (
    <main className="min-h-screen bg-gray-50 p-10">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "Product Comparison",
          url: "https://letrusto.com/compare",
          description: "Compare two products side by side with AI analysis, key specs, and value insights.",
        }}
      />
      <Script id="compare-breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold text-center mb-3">
          Product Comparison
        </h1>

        <p className="text-center text-gray-500 mb-12">
          Compare products side by side using LeTrusto AI
        </p>

        <form className="mb-10 grid gap-4 rounded-[2rem] border border-purple-100 bg-white p-6 shadow-sm md:grid-cols-3" method="get">
          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="first">
              First Product
            </label>
            <select id="first" name="first" defaultValue={firstProduct.id} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              {catalog.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="second">
              Second Product
            </label>
            <select id="second" name="second" defaultValue={secondProduct.id} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              {catalog.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button className="w-full rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-6 py-3 font-semibold text-white transition hover:from-fuchsia-700 hover:to-purple-700" type="submit">
              Compare Now
            </button>
          </div>
        </form>

        <div className="grid md:grid-cols-2 gap-6">

          {[firstProduct, secondProduct].map((product) => {
            const isWinner = winner.id === product.id;
            const isBestValue = valueWinner.id === product.id;
            return (
            <div
              key={product.name}
              className={`relative rounded-2xl border-2 bg-white p-6 shadow-sm transition ${isWinner ? "border-emerald-400 shadow-emerald-100" : "border-gray-100"}`}
            >
              {isWinner && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="flex items-center gap-1.5 rounded-full bg-emerald-500 px-4 py-1 text-sm font-bold text-white shadow-lg">
                    <Crown className="h-4 w-4" /> Best Overall
                  </span>
                </div>
              )}
              {!isWinner && isBestValue && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="flex items-center gap-1.5 rounded-full bg-blue-500 px-4 py-1 text-sm font-bold text-white shadow-lg">
                    <TrendingDown className="h-4 w-4" /> Best Value
                  </span>
                </div>
              )}
              <Image
                src={product.image}
                alt={product.name}
                width={240}
                height={200}
                unoptimized={product.image.startsWith("/images/products/")}
                className="mx-auto h-40 w-auto object-contain"
              />
              <h2 className="mt-4 text-center text-xl font-bold text-gray-900">{product.name}</h2>
              <p className="text-center text-sm text-gray-500">{product.brand}</p>
              <div className="mt-2 text-center text-2xl font-black text-purple-600">{product.price}</div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-purple-50 px-2 py-2">
                  <div className="text-xs font-semibold text-purple-500">AI Score</div>
                  <div className="text-lg font-black text-purple-700">{product.aiScore}</div>
                </div>
                <div className="rounded-xl bg-amber-50 px-2 py-2">
                  <div className="text-xs font-semibold text-amber-500">Rating</div>
                  <div className="text-lg font-black text-amber-700">{Number(product.rating).toFixed(1)}</div>
                </div>
                <div className="rounded-xl bg-emerald-50 px-2 py-2">
                  <div className="text-xs font-semibold text-emerald-500">Pros</div>
                  <div className="text-lg font-black text-emerald-700">{product.pros.length}</div>
                </div>
              </div>
              <ul className="mt-4 space-y-1.5">
                {product.features.slice(0, 4).map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-purple-100 text-xs text-purple-600">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
            );
          })}

        </div>

        <div className="mt-12 overflow-hidden rounded-[2rem] border border-purple-100 bg-white shadow-lg shadow-purple-100/40">
          <div className="border-b border-gray-100 px-6 py-5">
            <h2 className="text-2xl font-bold text-gray-900">Spec Comparison</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left">
              <thead className="sticky top-24 z-10 bg-gray-50 text-sm uppercase tracking-[0.2em] text-gray-400">
                <tr>
                  <th className="px-6 py-4">Spec</th>
                  <th className="px-6 py-4">{firstProduct.name}</th>
                  <th className="px-6 py-4">{secondProduct.name}</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-gray-100">
                  <td className="px-6 py-4 font-semibold text-gray-700">Price</td>
                  <td className={`px-6 py-4 ${valueWinner.id === firstProduct.id ? "bg-emerald-50 font-semibold text-emerald-700" : ""}`}>{firstProduct.price}</td>
                  <td className={`px-6 py-4 ${valueWinner.id === secondProduct.id ? "bg-emerald-50 font-semibold text-emerald-700" : ""}`}>{secondProduct.price}</td>
                </tr>
                <tr className="border-t border-gray-100">
                  <td className="px-6 py-4 font-semibold text-gray-700">Rating</td>
                  <td className={`px-6 py-4 ${firstProduct.rating >= secondProduct.rating ? "bg-purple-50 font-semibold text-purple-700" : ""}`}>{firstProduct.rating.toFixed(1)} / 5</td>
                  <td className={`px-6 py-4 ${secondProduct.rating >= firstProduct.rating ? "bg-purple-50 font-semibold text-purple-700" : ""}`}>{secondProduct.rating.toFixed(1)} / 5</td>
                </tr>
                <tr className="border-t border-gray-100">
                  <td className="px-6 py-4 font-semibold text-gray-700">AI Score</td>
                  <td className={`px-6 py-4 ${firstProduct.aiScore >= secondProduct.aiScore ? "bg-indigo-50 font-semibold text-indigo-700" : ""}`}>{firstProduct.aiScore}</td>
                  <td className={`px-6 py-4 ${secondProduct.aiScore >= firstProduct.aiScore ? "bg-indigo-50 font-semibold text-indigo-700" : ""}`}>{secondProduct.aiScore}</td>
                </tr>
                {specLabels.map((label) => (
                  <tr key={label} className="border-t border-gray-100">
                    <td className="px-6 py-4 font-semibold text-gray-700">{label}</td>
                    <td className={`px-6 py-4 ${firstSpecs.get(label) !== secondSpecs.get(label) ? "bg-amber-50/60" : ""}`}>{firstSpecs.get(label) ?? "-"}</td>
                    <td className={`px-6 py-4 ${firstSpecs.get(label) !== secondSpecs.get(label) ? "bg-amber-50/60" : ""}`}>{secondSpecs.get(label) ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-300 rounded-2xl mt-12 p-8">
          <h2 className="text-2xl font-bold text-purple-700 mb-4">
            🤖 LeTrusto AI Verdict
          </h2>

          <p className="text-lg">
            <b>Winner: {winner.name}</b>
          </p>

          <p className="mt-3 text-gray-700">
            {aiSummary.summary}
          </p>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-600">Key Advantages</p>
              <ul className="mt-2 space-y-2 text-gray-700">
                {aiSummary.keyAdvantages.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-600">Trade-offs</p>
              <ul className="mt-2 space-y-2 text-gray-700">
                {aiSummary.tradeOffs.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          </div>

        </div>

      </div>
    </main>
  );
}