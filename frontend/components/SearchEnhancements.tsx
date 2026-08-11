"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "letrusto:search-history";
const trendingSearches = [
  "best AI assistant for teams",
  "AI writing tool for SEO",
  "AI coding assistant",
  "AI video tool for creators",
  "best email marketing tool",
];

type SearchEnhancementsProps = {
  query: string;
};

export default function SearchEnhancements({ query }: SearchEnhancementsProps) {
  const [history] = useState<string[]>(() => {
    if (typeof window === "undefined") {
      return [];
    }

    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? (JSON.parse(raw) as string[]) : [];

      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });

  const visibleHistory = useMemo(() => {
    const normalized = query.trim();

    if (!normalized) {
      return history.filter((item) => item.trim().length > 0);
    }

    return [normalized, ...history.filter((item) => item !== normalized)].slice(0, 8);
  }, [history, query]);

  useEffect(() => {
    if (!query.trim()) {
      return;
    }

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(visibleHistory));
  }, [query, visibleHistory]);

  return (
    <section className="mb-8 rounded-3xl border border-purple-100 bg-white p-6 premium-shadow">
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Trending Searches</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {trendingSearches.map((item) => (
              <Link
                key={item}
                href={`/search?q=${encodeURIComponent(item)}`}
                className="rounded-full border border-purple-200 bg-purple-50 px-3 py-1.5 text-sm font-medium text-purple-700 transition hover:bg-purple-100"
              >
                {item}
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900">Search History</h3>
          {visibleHistory.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {visibleHistory.map((item) => (
                <Link
                  key={item}
                  href={`/search?q=${encodeURIComponent(item)}`}
                  className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
                >
                  {item}
                </Link>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No search history yet. Try a few searches and they will appear here.</p>
          )}
        </div>
      </div>
    </section>
  );
}
