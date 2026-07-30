export default function ProductCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-3xl border border-purple-100 bg-white p-6 premium-shadow">
      <div className="h-52 rounded-2xl shimmer" />
      <div className="mt-5 h-7 w-2/3 rounded-lg shimmer" />
      <div className="mt-3 h-4 w-full rounded-lg shimmer" />
      <div className="mt-2 h-4 w-4/5 rounded-lg shimmer" />

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="h-16 rounded-2xl shimmer" />
        <div className="h-16 rounded-2xl shimmer" />
      </div>

      <div className="mt-5 flex gap-3">
        <div className="h-12 flex-1 rounded-2xl shimmer" />
        <div className="h-12 flex-1 rounded-2xl shimmer" />
      </div>
    </div>
  );
}
