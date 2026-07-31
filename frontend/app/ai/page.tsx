import ProductCard from "@/components/ProductCard";
import { getAiRecommendations } from "@/services/product.service";

type Props = {
  searchParams: Promise<{
    q?: string;
  }>;
};

export default async function AIPage({ searchParams }: Props) {
  const { q = "" } = await searchParams;
  const recommendations = await getAiRecommendations(q);

  return (
    <main className="min-h-screen bg-gray-50 py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">
          🤖 LeTrusto AI Recommendation
        </h1>

        <p className="text-gray-500 mb-10">
          Your search: <span className="font-semibold">{q}</span>
        </p>

        {recommendations.length > 0 ? (
          <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
            {recommendations.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                highlightLabel="AI Recommended"
                priority
              />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-dashed border-purple-200 bg-white p-10 text-center shadow-lg shadow-purple-100/40">
            <div className="mx-auto max-w-xl">
              <span className="inline-flex rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-purple-700">
                AI Recommendation
              </span>
              <h2 className="mt-5 text-3xl font-bold text-gray-900">
                No suitable product found.
              </h2>
              <p className="mt-3 text-gray-500">
                Try keywords like iphone, android, coding, developer, music, or noise cancellation.
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}