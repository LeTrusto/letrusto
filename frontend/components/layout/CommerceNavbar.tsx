"use client";

import Link from "next/link";
import { useState } from "react";
import { Search, ShoppingBag, Heart, User, X } from "lucide-react";
import { useCart } from "@/lib/cartContext";

export default function CommerceNavbar() {
  const { itemCount } = useCart();
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
    <header className="sticky top-0 z-50 bg-white border-b border-[var(--border)]">
      {/* Mobile header */}
      <div className="md:hidden flex items-center justify-between h-14 px-4">
        <Link href="/" className="text-lg font-extrabold tracking-tight text-[var(--text-primary)]">
          LeTrusto
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="p-2 -m-2"
            aria-label="Search"
          >
            <Search size={20} strokeWidth={2} />
          </button>
          <Link href="/cart" className="relative p-2 -m-2" aria-label="Cart">
            <ShoppingBag size={20} strokeWidth={2} />
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
        <div className="md:hidden px-4 pb-3">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search beauty, jewellery, style..."
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
      <div className="hidden md:flex items-center justify-between h-16 max-w-7xl mx-auto px-6">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-extrabold tracking-tight text-[var(--text-primary)]">
            LeTrusto
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium text-[var(--text-secondary)]">
            <Link href="/shop" className="hover:text-[var(--text-primary)] transition-colors">
              Shop
            </Link>
            <Link href="/shop?category=jewellery" className="hover:text-[var(--text-primary)] transition-colors">
              Jewellery
            </Link>
            <Link href="/shop?category=hair-style" className="hover:text-[var(--text-primary)] transition-colors">
              Hair & Style
            </Link>
            <Link href="/shop?category=beauty-tools" className="hover:text-[var(--text-primary)] transition-colors">
              Beauty Tools
            </Link>
            <Link href="/deals" className="hover:text-[var(--text-primary)] transition-colors">
              Offers
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <form onSubmit={handleSearch} className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search..."
              className="lt-input pl-9 w-56 text-sm"
            />
          </form>
          <Link href="/favorites" className="p-2 hover:bg-[var(--surface-muted)] rounded-lg transition-colors" aria-label="Wishlist">
            <Heart size={20} strokeWidth={1.5} />
          </Link>
          <Link href="/cart" className="relative p-2 hover:bg-[var(--surface-muted)] rounded-lg transition-colors" aria-label="Cart">
            <ShoppingBag size={20} strokeWidth={1.5} />
            {itemCount > 0 && (
              <span className="absolute top-0.5 right-0.5 w-4.5 h-4.5 bg-[var(--lt-primary)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {itemCount > 9 ? "9+" : itemCount}
              </span>
            )}
          </Link>
          <Link href="/account" className="p-2 hover:bg-[var(--surface-muted)] rounded-lg transition-colors" aria-label="Account">
            <User size={20} strokeWidth={1.5} />
          </Link>
        </div>
      </div>
    </header>
  );
}
