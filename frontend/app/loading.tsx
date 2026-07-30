import ProductCardSkeleton from "@/components/ProductCardSkeleton";

export default function RootLoading() {
  return (
    <main className="min-h-screen px-6 py-14">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10 rounded-[2rem] bg-white p-8 premium-shadow">
          <div className="h-5 w-40 rounded-lg shimmer" />
          <div className="mt-4 h-12 w-2/3 rounded-xl shimmer" />
          <div className="mt-3 h-5 w-3/4 rounded-xl shimmer" />
        </div>

        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </main>
  );
}
