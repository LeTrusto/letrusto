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
    <header className="sticky top-0 z-50 border-b border-[#e9e4dc] bg-[#faf9f7] shadow-[0_1px_8px_rgba(24,24,27,0.035)]">
      {/* Mobile header */}
      <div className="flex h-[72px] items-center justify-between px-4 lg:hidden">
        <BrandMark compact />
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[rgba(212,165,116,0.16)] hover:text-[var(--text-primary)]"
            aria-label="Search"
          >
            <Search size={26} strokeWidth={2} />
          </button>
          <Link href="/cart" className="relative flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[rgba(212,165,116,0.16)] hover:text-[var(--text-primary)]" aria-label="Cart">
            <ShoppingBag size={26} strokeWidth={2} />
            {itemCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4.5 h-4.5 bg-[var(--lt-primary)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
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
      <div className="mx-auto hidden h-[130px] max-w-[1440px] items-center justify-between px-6 xl:px-8 lg:flex">
        <div className="flex min-w-0 items-center gap-4 xl:gap-5">
          <BrandMark />
          <nav className="flex items-center gap-0.5 text-[17px] font-medium" aria-label="Primary navigation">
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
              className="h-12 w-[248px] rounded-lg border-[#ded8cf] bg-[#fcfaf8] pl-10 text-[15px] shadow-none"
            />
          </form>
          <Link href="/favorites" className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[rgba(225,29,72,0.1)] hover:text-[var(--lt-rose)]" aria-label="Wishlist">
            <Heart size={27} strokeWidth={2} />
          </Link>
          <Link href="/cart" className="relative flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[rgba(212,165,116,0.16)] hover:text-[var(--text-primary)]" aria-label="Cart">
            <ShoppingBag size={27} strokeWidth={2} />
            {itemCount > 0 && (
              <span className="absolute top-0.5 right-0.5 w-4.5 h-4.5 bg-[var(--lt-primary)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {itemCount > 9 ? "9+" : itemCount}
              </span>
            )}
          </Link>
          <Link href="/account" className="flex h-12 w-12 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors duration-200 hover:bg-[rgba(212,165,116,0.16)] hover:text-[var(--text-primary)]" aria-label="Account">
            <User size={27} strokeWidth={2} />
          </Link>
        </div>
      </div>
    </header>
  );
}

function NavbarFallback() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#e9e4dc] bg-[#faf9f7] shadow-[0_1px_8px_rgba(24,24,27,0.035)]">
      <div className="flex h-[72px] items-center justify-between px-4 lg:hidden"><BrandMark compact /></div>
      <div className="mx-auto hidden h-[130px] max-w-7xl items-center px-6 xl:max-w-[1440px] xl:px-8 lg:flex"><BrandMark /></div>
    </header>
  );
}

function navClass(active: boolean) {
  return `relative rounded-md px-3 py-2.5 transition-colors ${
    active
      ? "bg-[rgba(212,165,116,0.15)] font-semibold text-[var(--lt-accent-dark)] after:absolute after:inset-x-3 after:-bottom-[1px] after:h-0.5 after:rounded-full after:bg-[var(--lt-accent-dark)]"
      : "text-[var(--text-secondary)] hover:bg-[rgba(212,165,116,0.1)] hover:text-[var(--text-primary)] hover:font-semibold"
  }`;
}
