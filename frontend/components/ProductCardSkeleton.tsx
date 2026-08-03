export default function ProductCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
      {/* Image area */}
      <div className="p-5">
        <div className="h-40 rounded-xl shimmer" />
      </div>
      {/* Content */}
      <div className="px-4 pb-4">
        <div className="mb-2.5 flex items-center justify-between">
          <div className="h-5 w-20 rounded-full shimmer" />
          <div className="h-5 w-10 rounded-full shimmer" />
        </div>
        <div className="h-5 w-3/4 rounded-lg shimmer" />
        <div className="mt-1.5 h-3.5 w-1/3 rounded-lg shimmer" />
        <div className="mt-3 flex items-end justify-between gap-2">
          <div className="h-4 w-24 rounded shimmer" />
          <div className="h-5 w-16 rounded shimmer" />
        </div>
        <div className="mt-4 flex gap-2">
          <div className="h-10 flex-1 rounded-xl shimmer" />
          <div className="h-10 w-10 rounded-xl shimmer" />
        </div>
      </div>
    </div>
  );
}
