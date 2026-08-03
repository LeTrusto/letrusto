import ProductCardSkeleton from "@/components/ProductCardSkeleton";

export default function RootLoading() {
  return (
    <main className="min-h-screen px-6 py-14">
      <div className="mx-auto max-w-7xl">
        {/* Hero skeleton */}
        <div className="mb-12 text-center">
          <div className="mx-auto h-6 w-48 rounded-full shimmer" />
          <div className="mx-auto mt-5 h-14 w-2/3 rounded-xl shimmer" />
          <div className="mx-auto mt-4 h-5 w-1/2 rounded-xl shimmer" />
          <div className="mx-auto mt-6 h-14 max-w-lg rounded-2xl shimmer" />
        </div>

        {/* Section heading */}
        <div className="mb-6">
          <div className="h-7 w-48 rounded-lg shimmer" />
          <div className="mt-2 h-4 w-72 rounded shimmer" />
        </div>

        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </main>
  );
}
