"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { Search, ShoppingBag, Heart, User, X } from "lucide-react";
import { useCart } from "@/lib/cartContext";
import BrandMark from "./BrandMark";

export default function CommerceNavbar() {
  return (
    <Suspense fallback={<NavbarFallback />}>
      <CommerceNavbarContent />
    </Suspense>
  );
}

function CommerceNavbarContent() {
  const { itemCount } = useCart();
  const pathname = usePathname();
  const activeCategory = useSearchParams().get("category") ?? "";
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState("");

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (query.trim()) {
      window.location.href = `/shop?q=${encodeURIComponent(query.trim())}`;
      setSearchOpen(false);
      setQuery("");
    }
  }

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--surface)] shadow-[0_2px_8px_rgba(107,33,168,0.08)]">
      {/* Mobile header */}
      <div className="flex h-[68px] items-center justify-between px-4 lg:hidden">
        <BrandMark compact />
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[var(--lt-purple)]/10 hover:text-[var(--lt-primary)]"
            aria-label="Search"
          >
            <Search size={26} strokeWidth={2} />
          </button>
          <Link href="/cart" className="relative flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[var(--lt-pink)]/10 hover:text-[var(--lt-accent)]" aria-label="Cart">
            <ShoppingBag size={26} strokeWidth={2} />
            {itemCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4.5 h-4.5 bg-[var(--lt-accent)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {itemCount > 9 ? "9+" : itemCount}
              </span>
            )}
          </Link>
        </div>
      </div>

      {/* Mobile search overlay */}
      {searchOpen && (
        <div className="px-4 pb-3 lg:hidden">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search designs, apparel, wall art..."
              className="lt-input flex-1"
              autoFocus
            />
            <button type="button" onClick={() => setSearchOpen(false)} className="p-2" aria-label="Close search">
              <X size={20} />
            </button>
          </form>
        </div>
      )}

      {/* Desktop header */}
      <div className="mx-auto hidden h-[88px] max-w-[1280px] items-center justify-between px-6 lg:flex">
        <div className="flex min-w-0 items-center gap-4 xl:gap-5">
          <BrandMark />
          <nav className="flex items-center gap-0.5 text-[16px] font-medium" aria-label="Primary navigation">
            <Link href="/shop" className={navClass(pathname === "/shop" && !activeCategory)}>
              Shop
            </Link>
            <Link href="/shop?category=apparel" className={navClass(activeCategory === "apparel")}>
              Apparel
            </Link>
            <Link href="/shop?category=wall-art" className={navClass(activeCategory === "wall-art")}>
              Wall Art
            </Link>
            <Link href="/shop?category=accessories" className={navClass(activeCategory === "accessories")}>
              Accessories
            </Link>
            <Link href="/shop?category=home-living" className={navClass(activeCategory === "home-living")}>
              Home & Living
            </Link>
          </nav>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <form onSubmit={handleSearch} className="relative">
            <Search size={21} strokeWidth={2} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search..."
              className="h-11 w-[240px] rounded-lg border border-[var(--border)] bg-[var(--surface-soft)] pl-10 text-[14px] placeholder-[var(--text-muted)]"
            />
          </form>
          <Link href="/favorites" className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[var(--lt-pink)]/10 hover:text-[var(--lt-accent)]" aria-label="Wishlist">
            <Heart size={21} strokeWidth={2} />
          </Link>
          <Link href="/cart" className="relative flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[var(--lt-pink)]/10 hover:text-[var(--lt-accent)]" aria-label="Cart">
            <ShoppingBag size={21} strokeWidth={2} />
            {itemCount > 0 && (
              <span className="absolute top-0.5 right-0.5 w-4.5 h-4.5 bg-[var(--lt-accent)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {itemCount > 9 ? "9+" : itemCount}
              </span>
            )}
          </Link>
          <Link href="/account" className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[var(--lt-purple)]/10 hover:text-[var(--lt-primary)]" aria-label="Account">
            <User size={21} strokeWidth={2} />
          </Link>
        </div>
      </div>
    </header>
  );
}

function NavbarFallback() {
  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--surface)] shadow-[0_2px_8px_rgba(107,33,168,0.08)]">
      <div className="flex h-[68px] items-center justify-between px-4 lg:hidden"><BrandMark compact /></div>
      <div className="mx-auto hidden h-[88px] max-w-[1280px] items-center px-6 lg:flex"><BrandMark /></div>
    </header>
  );
}

function navClass(active: boolean) {
  return `relative rounded-md px-3 py-2.5 transition-colors ${
    active
      ? "bg-[var(--lt-purple)]/15 font-semibold text-[var(--lt-primary)] after:absolute after:inset-x-3 after:-bottom-[1px] after:h-0.5 after:rounded-full after:bg-[var(--lt-accent)]"
      : "text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)] hover:font-semibold"
  }`;
}
