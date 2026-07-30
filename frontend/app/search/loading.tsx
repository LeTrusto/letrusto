import ProductCardSkeleton from "@/components/ProductCardSkeleton";

export default function SearchLoading() {
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10 rounded-[2rem] bg-white p-8 premium-shadow">
          <div className="h-5 w-48 rounded-lg shimmer" />
          <div className="mt-4 h-10 w-1/2 rounded-lg shimmer" />
          <div className="mt-3 h-4 w-3/4 rounded-lg shimmer" />
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
