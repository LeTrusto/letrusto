"use client";

import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { products } from "@/lib/products";

const trendingSearches = [
  "phone under 30000",
  "laptop for coding",
  "headphones for office",
  "camera for travel",
];

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const router = useRouter();
  const suggestions = useMemo(() => {
    return [
      ...trendingSearches,
      ...products.slice(0, 12).map((product) => product.name),
    ];
  }, []);

  const handleSearch = () => {
    if (!query.trim()) return;

    try {
      const key = "letrusto:search-history";
      const raw = window.localStorage.getItem(key);
      const parsed = raw ? (JSON.parse(raw) as string[]) : [];
      const next = [query.trim(), ...parsed.filter((item) => item !== query.trim())].slice(0, 8);
      window.localStorage.setItem(key, JSON.stringify(next));
    } catch {
      // no-op
    }

    router.push(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="relative z-20 flex justify-center -mt-10 px-4">
      <div className="w-full max-w-4xl rounded-[1.75rem] border border-purple-100 bg-white p-3 premium-shadow">
        <div className="flex items-center gap-2">
          <Search className="ml-2 h-5 w-5 text-purple-500" />
        <input
          type="text"
          list="search-suggestions"
          aria-label="Search products"
          placeholder="Search products, compare phones, laptops, cameras..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSearch();
            }
          }}
          className="flex-1 rounded-2xl px-4 py-4 text-base outline-none md:text-lg"
        />

        <button
          onClick={handleSearch}
          className="rounded-2xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-6 py-4 text-sm font-semibold text-white transition hover:scale-[1.01] md:px-8 md:text-base"
        >
          Search
        </button>
        </div>

        <datalist id="search-suggestions">
          {suggestions.map((item) => (
            <option key={item} value={item} />
          ))}
        </datalist>

        <div className="mt-3 flex flex-wrap gap-2 px-2 pb-1">
          {trendingSearches.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => {
                setQuery(item);
                router.push(`/search?q=${encodeURIComponent(item)}`);
              }}
              className="rounded-full bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700 transition hover:bg-purple-100"
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}