import Link from "next/link";

export default function CompareSection() {
  return (
    <section className="bg-white py-20">
      <div className="mx-auto max-w-6xl rounded-[2rem] border border-purple-100 bg-gradient-to-r from-slate-900 via-purple-950 to-fuchsia-950 px-6 py-12 text-white shadow-2xl shadow-purple-200 md:px-10">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-pink-200">
          Side-by-side clarity
        </p>
        <div className="mt-4 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <h2 className="text-4xl font-bold md:text-5xl">Compare products with context, not guesswork.</h2>
            <p className="mt-4 text-lg text-purple-100">
              Open a ready-made comparison, inspect specs, and let LeTrusto surface the stronger fit for your budget and use case.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              href="/compare?first=iphone16pro&second=galaxy-s25"
              className="inline-flex items-center justify-center rounded-2xl bg-white px-6 py-3 font-semibold text-purple-700 transition hover:bg-purple-50"
            >
              Compare Phones
            </Link>
            <Link
              href="/compare?first=macbook-air-m4&second=sony-wh-1000xm6"
              className="inline-flex items-center justify-center rounded-2xl border border-white/20 px-6 py-3 font-semibold text-white transition hover:bg-white/10"
            >
              Explore Discovery
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}