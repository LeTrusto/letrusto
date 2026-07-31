"use client";

import { Heart, LayoutGrid, Search, Sparkles, Scale } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useFavorites } from "@/hooks/useFavorites";

export default function Navbar() {
  const { favoriteIds } = useFavorites();
  const pathname = usePathname();

  const navItemClass =
    "inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[15px] font-semibold tracking-[0.01em] text-slate-700 transition hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-700";

  const activeNavItemClass = "bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 shadow-sm";

  return (
    <header className="sticky top-0 z-50 border-b border-white/60 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:gap-5">
        <Link href="/" className="flex min-w-0 items-center gap-3 self-start lg:self-center">
          <Image
            src="/images/logo/logo.png"
            alt="LeTrusto"
            width={86}
            height={76}
            priority
            className="h-14 w-auto sm:h-16"
          />

          <div className="min-w-0">
            <h1 className="truncate text-3xl font-black leading-none sm:text-4xl lg:text-[2.5rem]">
              <span className="text-pink-600">Le</span>
              <span className="text-slate-900">Trusto</span>
            </h1>

            <p className="truncate text-sm font-medium text-gray-500 sm:text-base">
              Know Before You Buy
            </p>
          </div>
        </Link>

        <nav className="flex w-full flex-wrap items-center gap-2 sm:gap-3 lg:w-auto lg:flex-1 lg:justify-center">
          <Link href="/" className={`${navItemClass} ${pathname === "/" ? activeNavItemClass : ""}`}>
            Home
          </Link>

          <Link href="/#categories" className={navItemClass}>
            <LayoutGrid className="h-4 w-4" />
            Categories
          </Link>

          <Link href="/compare" className={`${navItemClass} ${pathname === "/compare" ? activeNavItemClass : ""}`}>
            <Scale className="h-4 w-4" />
            Compare
          </Link>

          <Link href="/ai" className={`${navItemClass} ${pathname === "/ai" ? activeNavItemClass : ""}`}>
            <Sparkles className="h-4 w-4" />
            AI Assistant
          </Link>

          <Link href="/favorites" className={`${navItemClass} ${pathname === "/favorites" ? activeNavItemClass : ""}`}>
            <Heart className="h-4 w-4" />
            Favorites
            <span className="rounded-full bg-pink-100 px-2 py-0.5 text-xs font-semibold text-pink-600">
              {favoriteIds.length}
            </span>
          </Link>

          <Link href="/search" className={`${navItemClass} ${pathname === "/search" ? activeNavItemClass : ""}`}>
            <Search className="h-4 w-4" />
            Search
          </Link>
        </nav>

        <div className="flex w-full flex-wrap items-center gap-3 sm:w-auto sm:self-start lg:w-auto lg:justify-end lg:self-center">
          <Link
            href="/search"
            className="rounded-xl border border-purple-200 bg-white px-4 py-2.5 text-sm font-semibold text-purple-700 transition hover:bg-purple-50"
          >
            Explore Products
          </Link>
          <Link
            href="/ai"
            className="rounded-xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:scale-[1.02]"
          >
            Ask AI
          </Link>
        </div>
      </div>
    </header>
  );
}