import type { ProductReview } from "@/types/products";

type ProductReviewsProps = {
  overallRating: number;
  reviewSummary: string;
  reviews: ProductReview[];
};

export default function ProductReviews({
  overallRating,
  reviewSummary,
  reviews,
}: ProductReviewsProps) {
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
        <p className="mt-3 leading-7 text-purple-900">{reviewSummary}</p>
      </div>

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
