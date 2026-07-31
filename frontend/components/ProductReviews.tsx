import type { ProductReview } from "@/types/products";

type AIReviewInsights = {
  positives: string[];
  negatives: string[];
  buyingAdvice: string;
  finalVerdict: string;
};

type AIBuyingGuideInsights = {
  worthBuying: boolean;
  verdict: string;
  bestFor: string[];
  priceValueAnalysis: string;
};

type ProductReviewsProps = {
  overallRating: number;
  reviewSummary: string;
  reviews: ProductReview[];
  aiReviewInsights?: AIReviewInsights;
  aiBuyingGuide?: AIBuyingGuideInsights;
};

export default function ProductReviews({
  overallRating,
  reviewSummary,
  reviews,
  aiReviewInsights,
  aiBuyingGuide,
}: ProductReviewsProps) {
  const summaryText = aiReviewInsights?.finalVerdict || reviewSummary;

  return (
    <section className="rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Reviews</h2>
          <p className="mt-2 text-gray-500">Five sample reviews and an AI summary of buyer sentiment.</p>
        </div>

        <div className="rounded-2xl bg-amber-50 px-5 py-4 text-amber-700">
          <p className="text-sm font-semibold uppercase tracking-[0.2em]">Overall Rating</p>
          <p className="mt-1 text-3xl font-bold">{overallRating.toFixed(1)} / 5</p>
        </div>
      </div>

      <div className="mb-8 rounded-3xl border border-purple-100 bg-purple-50 p-6">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-600">AI Review Summary</p>
        <p className="mt-3 leading-7 text-purple-900">{summaryText}</p>
      </div>

      {aiReviewInsights ? (
        <div className="mb-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">What Buyers Like</p>
            <ul className="mt-2 space-y-2 text-emerald-900">
              {aiReviewInsights.positives.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-rose-700">Watch-outs</p>
            <ul className="mt-2 space-y-2 text-rose-900">
              {aiReviewInsights.negatives.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      {aiBuyingGuide ? (
        <div className="mb-8 rounded-3xl border border-indigo-100 bg-indigo-50 p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-700">AI Buying Guide</p>
          <p className="mt-3 text-indigo-900">{aiBuyingGuide.verdict}</p>
          <p className="mt-3 text-sm text-indigo-900">{aiBuyingGuide.priceValueAnalysis}</p>
          <p className="mt-3 text-sm font-semibold text-indigo-800">
            {aiBuyingGuide.worthBuying ? "Worth buying for the right buyer profile." : "Consider alternatives before buying."}
          </p>
          {aiBuyingGuide.bestFor.length > 0 ? (
            <ul className="mt-2 space-y-1 text-sm text-indigo-900">
              {aiBuyingGuide.bestFor.map((item) => (
                <li key={item}>• Best for: {item}</li>
              ))}
            </ul>
          ) : null}
          {aiReviewInsights?.buyingAdvice ? (
            <p className="mt-3 text-sm text-indigo-900">{aiReviewInsights.buyingAdvice}</p>
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
        {reviews.map((review) => (
          <article key={`${review.author}-${review.date}`} className="rounded-3xl border border-gray-100 bg-gray-50 p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-gray-900">{review.author}</h3>
                <p className="text-sm text-gray-400">{review.date}</p>
              </div>
              <div className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-amber-600">
                {review.rating.toFixed(1)}
              </div>
            </div>
            <p className="mt-4 font-semibold text-gray-900">{review.title}</p>
            <p className="mt-2 text-sm leading-6 text-gray-600">{review.comment}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
