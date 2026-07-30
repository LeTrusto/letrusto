"use client";

import { Heart, LayoutGrid, Search, Sparkles, Scale } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

import { useFavorites } from "@/hooks/useFavorites";

export default function Navbar() {
  const { favoriteIds } = useFavorites();

  return (
    <header className="sticky top-0 z-50 border-b border-white/60 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex min-h-20 max-w-7xl flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between">
        <Link href="/" className="flex items-center gap-3">
          <Image
            src="/images/logo/logo.png"
            alt="LeTrusto"
            width={100}
            height={90}
            priority
          />

          <div>
            <h1 className="text-3xl font-extrabold leading-none md:text-5xl">
              <span className="text-pink-600">Le</span>
              <span className="text-slate-900">Trusto</span>
            </h1>

            <p className="text-sm text-gray-500 md:text-base">
              Know Before You Buy
            </p>
          </div>
        </Link>

        <nav className="flex flex-wrap items-center gap-3 text-sm font-medium text-gray-700 md:text-base">
          <Link href="/" className="rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            Home
          </Link>

          <Link href="/#categories" className="inline-flex items-center gap-2 rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            <LayoutGrid className="h-4 w-4" />
            Categories
          </Link>

          <Link href="/compare" className="inline-flex items-center gap-2 rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            <Scale className="h-4 w-4" />
            Compare
          </Link>

          <Link href="/ai" className="inline-flex items-center gap-2 rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            <Sparkles className="h-4 w-4" />
            AI Assistant
          </Link>

          <Link href="/favorites" className="inline-flex items-center gap-2 rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            <Heart className="h-4 w-4" />
            Favorites
            <span className="rounded-full bg-pink-100 px-2 py-0.5 text-xs font-semibold text-pink-600">
              {favoriteIds.length}
            </span>
          </Link>

          <Link href="/search" className="inline-flex items-center gap-2 rounded-full px-3 py-2 transition hover:bg-purple-50 hover:text-purple-600">
            <Search className="h-4 w-4" />
            Search
          </Link>
        </nav>

        <div className="flex items-center gap-3 self-start lg:self-auto">
          <Link
            href="/search"
            className="rounded-xl border border-purple-200 px-4 py-2 font-medium text-purple-700 transition hover:bg-purple-50"
          >
            Explore Products
          </Link>
          <Link
            href="/ai"
            className="rounded-xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-5 py-2 font-semibold text-white transition hover:scale-[1.02]"
          >
            Ask AI
          </Link>
        </div>
      </div>
    </header>
  );
}