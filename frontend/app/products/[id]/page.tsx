import Link from "next/link";

import ProductCard from "@/components/ProductCard";
import PriceHistoryChart from "@/components/PriceHistoryChart";
import ProductBuyButtons from "@/components/ProductBuyButtons";
import ProductImageGallery from "@/components/ProductImageGallery";
import ProductReviews from "@/components/ProductReviews";
import RecentlyViewedProducts from "@/components/RecentlyViewedProducts";
import { categoryLabels } from "@/lib/products";
import { getAIBuyingGuide, getAIReviewSummary } from "@/services/ai.service";
import { getAllProducts, getProductById, getRelatedProductsByProductId } from "@/services/product.service";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const catalog = await getAllProducts();
  const fallbackProduct = catalog[0];
  const product = (await getProductById(id)) ?? fallbackProduct;
  const [relatedProducts, aiReviewSummary, aiBuyingGuide] = await Promise.all([
    getRelatedProductsByProductId(product.id, 4),
    getAIReviewSummary(product.id),
    getAIBuyingGuide(product.id, 3),
  ]);

  return (
    <main className="min-h-screen bg-gray-50 p-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-purple-500">Product Details</p>
            <h1 className="mt-2 text-4xl font-bold text-gray-900 md:text-5xl">{product.name}</h1>
            <p className="mt-3 text-lg text-gray-500">{product.brand} • {categoryLabels[product.category]} • {product.availability}</p>
          </div>

          <Link
            href={`/compare?first=${product.id}`}
            className="inline-flex items-center justify-center rounded-2xl border border-purple-200 bg-white px-5 py-3 font-semibold text-purple-700 transition hover:bg-purple-50"
          >
            Compare This Product
          </Link>
        </div>

        <div className="grid gap-10 xl:grid-cols-[1.05fr_0.95fr]">
          <ProductImageGallery name={product.name} images={product.images} fallbackImage={product.fallbackImage} />

          <div className="min-w-0 space-y-6 xl:sticky xl:top-28 xl:self-start">
            <div className="rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-purple-700">
                  {categoryLabels[product.category]}
                </span>
                <span className="rounded-full bg-amber-100 px-4 py-2 text-sm font-semibold text-amber-700">
                  Rating {product.rating.toFixed(1)} / 5
                </span>
                <span className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">
                  AI Score {product.aiScore}/100
                </span>
              </div>

              <div className="mt-6 flex items-end justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-400">Price</p>
                  <div className="mt-1 text-5xl font-bold text-purple-600">{product.price}</div>
                </div>
                <div className="rounded-2xl bg-gray-50 px-4 py-3 text-right">
                  <p className="text-sm text-gray-400">Availability</p>
                  <p className="font-semibold text-gray-700">{product.availability}</p>
                </div>
              </div>

              <div className="mt-6 rounded-3xl border border-purple-100 bg-purple-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-600">AI Summary</p>
                <p className="mt-3 leading-7 text-purple-950">{product.aiSummary}</p>
              </div>

              <p className="mt-6 leading-7 text-gray-600">{product.description}</p>

              <div className="mt-8 grid gap-3 sm:grid-cols-2">
                {product.features.map((feature) => (
                  <div key={feature} className="flex items-center gap-3 rounded-2xl bg-gray-50 px-4 py-3 text-gray-700">
                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100 text-sm text-purple-700">✓</span>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
              <h2 className="mb-2 text-2xl font-bold text-gray-900">Buy Now</h2>
              <p className="mb-5 text-sm text-gray-400">Compare prices across retailers before you buy.</p>
              <ProductBuyButtons links={product.buyLinks} />
              <p className="mt-4 text-center text-xs text-gray-400">
                * LeTrusto may earn a small affiliate commission at no extra cost to you.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow-sm border border-emerald-100">
            <h2 className="flex items-center gap-2 text-xl font-bold text-gray-900">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 text-sm text-emerald-600">✓</span>
              Pros
            </h2>
            <ul className="mt-4 space-y-3">
              {product.pros.map((item) => (
                <li key={item} className="flex gap-3 rounded-xl bg-emerald-50 px-4 py-2.5 text-sm text-emerald-800">
                  <span className="mt-0.5 text-emerald-500">+</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-sm border border-rose-100">
            <h2 className="flex items-center gap-2 text-xl font-bold text-gray-900">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-rose-100 text-sm text-rose-600">✕</span>
              Cons
            </h2>
            <ul className="mt-4 space-y-3">
              {product.cons.map((item) => (
                <li key={item} className="flex gap-3 rounded-xl bg-rose-50 px-4 py-2.5 text-sm text-rose-800">
                  <span className="mt-0.5 text-rose-400">-</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Expert Verdict */}
        <div className="mt-6 rounded-2xl border border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 p-6">
          <div className="flex items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-600 text-lg">🤖</span>
            <div>
              <h2 className="text-lg font-bold text-purple-900">Expert Verdict</h2>
              <p className="mt-1.5 text-sm leading-relaxed text-purple-800">{product.aiSummary}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {product.bestFor.map((item) => (
                  <span key={item} className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
                    ✓ {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          <div className="rounded-[2rem] bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-900">Best For</h2>
            <ul className="mt-4 space-y-3 text-gray-600">
              {product.bestFor.map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="text-purple-500">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-[2rem] bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-900">Not Recommended For</h2>
            <ul className="mt-4 space-y-3 text-gray-600">
              {product.notRecommendedFor.map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="text-pink-500">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-12 rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
          <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Specifications</h2>
              <p className="mt-2 text-gray-500">Core specs and buying context for faster evaluation.</p>
            </div>
          </div>

          <div className="overflow-hidden rounded-3xl border border-gray-100">
            <table className="min-w-full text-left">
              <tbody>
                {product.specs.map((spec, index) => (
                  <tr key={spec.label} className={index === 0 ? "" : "border-t border-gray-100"}>
                    <td className="w-1/3 bg-gray-50 px-5 py-4 font-semibold text-gray-700">{spec.label}</td>
                    <td className="px-5 py-4 text-gray-600">{spec.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-12 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <PriceHistoryChart points={product.priceHistory} />

          <div className="rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
            <h2 className="text-3xl font-bold text-gray-900">Compare From Here</h2>
            <p className="mt-2 text-gray-500">Pick another product directly from this page and jump into a side-by-side view.</p>

            <form className="mt-6 space-y-4" action="/compare" method="get">
              <input type="hidden" name="first" value={product.id} />
              <label className="block text-sm font-semibold text-gray-700" htmlFor="second-product">
                Select another product
              </label>
              <select
                id="second-product"
                name="second"
                defaultValue={relatedProducts[0]?.id ?? catalog.find((item) => item.id !== product.id)?.id}
                className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400"
              >
                {catalog
                  .filter((item) => item.id !== product.id)
                  .map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
              </select>

              <button className="w-full rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-6 py-3 font-semibold text-white transition hover:from-fuchsia-700 hover:to-purple-700" type="submit">
                Compare Products
              </button>
            </form>
          </div>
        </div>

        <div className="mt-12">
          <ProductReviews
            overallRating={product.rating}
            reviewSummary={product.reviewSummary}
            reviews={product.reviews}
            aiReviewInsights={aiReviewSummary}
            aiBuyingGuide={aiBuyingGuide}
          />
        </div>

        <section className="mt-16 space-y-6">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Similar Products</h2>
              <p className="text-gray-500">Four related options based on category, tags, and overall fit.</p>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {relatedProducts.map((relatedProduct) => (
              <ProductCard
                key={relatedProduct.id}
                product={relatedProduct}
                compareWithId={product.id}
                highlightLabel="Related Pick"
              />
            ))}
          </div>
        </section>

        <RecentlyViewedProducts currentProductId={product.id} />
      </div>
    </main>
  );
}
