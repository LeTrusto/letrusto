import Link from "next/link";

export default function CompareSection() {
  return (
    <section className="bg-white py-20">
      <div className="mx-auto max-w-6xl rounded-[var(--radius-2xl)] border border-[var(--border)] bg-gradient-to-r from-slate-900 via-purple-950 to-fuchsia-950 px-6 py-12 text-white shadow-[var(--shadow-premium)] md:px-10">
        <p className="lt-label text-purple-300">
          Side-by-side clarity
        </p>
        <div className="mt-4 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <h2 className="text-4xl font-bold md:text-5xl">Compare AI tools with context, not guesswork.</h2>
            <p className="mt-4 text-lg text-purple-100">
              Open a side-by-side comparison, inspect features and pricing, and let LeTrusto surface the stronger fit for your workflow.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              href="/compare"
              className="lt-btn lt-btn-lg bg-white text-[var(--lt-purple-dark)] hover:bg-purple-50"
            >
              Compare AI Tools
            </Link>
            <Link
              href="/ai-tools"
              className="lt-btn lt-btn-lg border-white/20 text-white hover:bg-white/10"
            >
              Browse Tools
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}