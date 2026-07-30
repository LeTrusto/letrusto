import type { ProductPriceHistoryPoint } from "@/types/products";

type PriceHistoryChartProps = {
  points: ProductPriceHistoryPoint[];
};

export default function PriceHistoryChart({ points }: PriceHistoryChartProps) {
  const prices = points.map((point) => point.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const spread = Math.max(maxPrice - minPrice, 1);

  return (
    <div className="rounded-[2rem] bg-white p-8 shadow-lg shadow-purple-100/40">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Price History</h2>
          <p className="mt-2 text-gray-500">Mock trend data to show how this product has moved over time.</p>
        </div>
        <div className="rounded-2xl bg-purple-50 px-4 py-3 text-sm text-purple-700">
          Range: ₹{minPrice.toLocaleString("en-IN")} to ₹{maxPrice.toLocaleString("en-IN")}
        </div>
      </div>

      <div className="grid grid-cols-6 items-end gap-4">
        {points.map((point) => {
          const height = 90 + ((point.price - minPrice) / spread) * 120;

          return (
            <div key={point.label} className="flex flex-col items-center gap-3">
              <div className="text-sm font-medium text-gray-500">₹{point.price.toLocaleString("en-IN")}</div>
              <div className="flex h-56 w-full items-end rounded-3xl bg-gray-50 px-3 pb-3">
                <div
                  className="w-full rounded-2xl bg-gradient-to-t from-fuchsia-600 to-purple-400"
                  style={{ height }}
                />
              </div>
              <div className="text-sm font-semibold text-gray-700">{point.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
