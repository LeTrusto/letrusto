export default function ProductDetailsLoading() {
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[2rem] bg-white p-8 premium-shadow">
            <div className="h-[28rem] rounded-3xl shimmer" />
          </div>
          <div className="space-y-6">
            <div className="rounded-[2rem] bg-white p-8 premium-shadow">
              <div className="h-8 w-1/2 rounded-lg shimmer" />
              <div className="mt-5 h-12 w-1/3 rounded-lg shimmer" />
              <div className="mt-4 h-4 w-full rounded-lg shimmer" />
              <div className="mt-2 h-4 w-5/6 rounded-lg shimmer" />
              <div className="mt-8 h-40 rounded-2xl shimmer" />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
