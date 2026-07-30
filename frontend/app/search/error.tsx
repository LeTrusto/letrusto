"use client";

type SearchErrorProps = {
  error: Error;
  reset: () => void;
};

export default function SearchError({ error, reset }: SearchErrorProps) {
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-3xl rounded-[2rem] border border-rose-200 bg-white p-8 text-center premium-shadow">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-rose-500">Search Error</p>
        <h1 className="mt-3 text-3xl font-bold text-gray-900">Something went wrong while loading products.</h1>
        <p className="mt-4 text-gray-600">{error.message}</p>
        <button
          type="button"
          onClick={reset}
          className="mt-8 rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-6 py-3 font-semibold text-white"
        >
          Try Again
        </button>
      </div>
    </main>
  );
}
