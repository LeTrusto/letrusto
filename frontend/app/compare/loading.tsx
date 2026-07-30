export default function CompareLoading() {
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="h-12 w-1/3 rounded-xl shimmer" />
        <div className="grid gap-8 md:grid-cols-2">
          <div className="h-[28rem] rounded-[2rem] shimmer" />
          <div className="h-[28rem] rounded-[2rem] shimmer" />
        </div>
        <div className="h-64 rounded-[2rem] shimmer" />
      </div>
    </main>
  );
}
