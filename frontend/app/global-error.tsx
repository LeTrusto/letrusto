"use client";

import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center gap-6 bg-white px-6 py-24 text-center font-sans">
        <span className="text-5xl">⚠️</span>
        <div>
          <h1 className="text-3xl font-black text-gray-900">Something went wrong</h1>
          <p className="mt-3 max-w-md text-gray-500">
            An unexpected error occurred. Our team has been notified. Please try again.
          </p>
          {process.env.NODE_ENV === "development" && (
            <p className="mt-2 rounded bg-red-50 px-3 py-2 text-xs text-red-600">{error.message}</p>
          )}
        </div>
        <div className="flex flex-wrap justify-center gap-3">
          <button
            onClick={reset}
            className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="rounded-xl border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700"
          >
            Back to Home
          </Link>
        </div>
      </body>
    </html>
  );
}
