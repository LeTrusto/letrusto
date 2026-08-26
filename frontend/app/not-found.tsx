import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Page Not Found" };

export default function NotFound() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-24 text-center">
      <div className="relative">
        <div className="pointer-events-none absolute inset-0 -z-10 rounded-full bg-purple-100 blur-3xl" />
        <span className="text-8xl font-black text-gray-100 md:text-[10rem]">404</span>
      </div>
      <div className="-mt-6">
        <h1 className="text-3xl font-black text-gray-900 md:text-4xl">Page not found</h1>
        <p className="mt-3 max-w-md text-gray-500">
          Looks like this page wandered off. Let our AI guide you back to something great.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-3">
        <Link
          href="/"
          className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white transition hover:scale-[1.02]"
        >
          Back to Home
        </Link>
        <Link
          href="/shop"
          className="rounded-xl border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700 transition hover:border-purple-300 hover:text-purple-700"
        >
          Browse Products
        </Link>
        <Link
          href="/how-it-works"
          className="rounded-xl border border-purple-200 bg-purple-50 px-6 py-3 text-sm font-semibold text-purple-700 transition hover:bg-purple-100"
        >
          How it works
        </Link>
      </div>
    </main>
  );
}
