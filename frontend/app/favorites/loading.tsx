import ProductCardSkeleton from "@/components/ProductCardSkeleton";

export default function FavoritesLoading() {
  return (
    <main className="min-h-screen px-6 py-14">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10 h-40 rounded-[2rem] shimmer" />
        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </main>
  );
}
