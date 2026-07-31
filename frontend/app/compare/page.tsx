import Image from "next/image";

import { getAIComparisonSummary } from "@/services/ai.service";
import { getAllProducts, getCompareProducts } from "@/services/product.service";
import { getSearchParamValue } from "@/utils/helpers";

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

  return (
    <main className="min-h-screen bg-gray-50 p-10">
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

        <div className="grid md:grid-cols-2 gap-10">

          {[firstProduct, secondProduct].map((product) => (
            <div
              key={product.name}
              className="bg-white rounded-2xl shadow-lg p-8"
            >
              <Image
                src={product.image}
                alt={product.name}
                width={300}
                height={300}
                unoptimized={product.image.startsWith("/images/products/")}
                className="mx-auto"
              />

              <h2 className="text-2xl font-bold mt-6 text-center">
                {product.name}
              </h2>

              <div className="text-center text-3xl font-bold text-purple-600 mt-2">
                {product.price}
              </div>

              <div className="mt-8 space-y-4">
                {product.features.slice(0, 4).map((feature) => (
                  <div key={feature} className="flex items-center gap-3">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-purple-100 text-sm text-purple-700">✓</span>
                    <span>{feature}</span>
                  </div>
                ))}

                <div className="flex justify-between font-bold text-purple-700">
                  <span>AI Score</span>
                  <span>{product.aiScore}/100</span>
                </div>

                <div className="flex justify-between text-gray-600">
                  <span>Rating</span>
                  <span>{product.rating.toFixed(1)} / 5</span>
                </div>

              </div>

            </div>
          ))}

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