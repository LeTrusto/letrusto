"use client";

import { Bell, Heart, LogIn, LogOut, Search, Sparkles, Scale, LayoutDashboard, Tag, User, Menu, X, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useFavorites } from "@/hooks/useFavorites";
import { CATALOG_TREE } from "@/constants/index";

export default function Navbar() {
  const { favoriteIds } = useFavorites();
  const pathname = usePathname();
  const { user, isLoading, logout } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [categoriesOpen, setCategoriesOpen] = useState(false);

  const navItemClass =
    "inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[15px] font-semibold tracking-[0.01em] text-slate-700 transition hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-700";

  const activeNavItemClass = "bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 shadow-sm";

  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/95 shadow-sm backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-3 sm:px-6">
        {/* Logo */}
        <Link href="/" className="flex shrink-0 items-center gap-2.5">
          <Image src="/images/logo/logo.png" alt="LeTrusto" width={60} height={52} priority className="h-10 w-auto" />
          <div className="hidden sm:block">
            <span className="text-2xl font-black leading-none">
              <span className="text-pink-600">Le</span>
              <span className="text-slate-900">Trusto</span>
            </span>
            <p className="text-[11px] font-medium text-gray-400">Know Before You Buy</p>
          </div>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 lg:flex">
          <Link href="/" className={`${navItemClass} ${pathname === "/" ? activeNavItemClass : ""}`}>Home</Link>

          {/* Categories dropdown */}
          <div className="relative">
            <button
              onClick={() => setCategoriesOpen((o) => !o)}
              className={`${navItemClass} gap-1`}
            >
              Categories
              <ChevronDown className={`h-3.5 w-3.5 transition ${categoriesOpen ? "rotate-180" : ""}`} />
            </button>
            {categoriesOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setCategoriesOpen(false)} />
                <div className="absolute left-0 top-12 z-50 w-80 rounded-2xl border border-gray-100 bg-white p-4 shadow-2xl">
                  <p className="mb-3 text-xs font-bold uppercase tracking-widest text-gray-400">Browse by Category</p>
                  <div className="grid grid-cols-2 gap-1.5">
                    {CATALOG_TREE[0]?.children?.slice(0, 8).map((cat) => (
                      <Link
                        key={cat.slug}
                        href={`/category/${cat.slug}`}
                        onClick={() => setCategoriesOpen(false)}
                        className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-purple-50 hover:text-purple-700"
                      >
                        <span>{cat.icon}</span>
                        {cat.name}
                      </Link>
                    ))}
                  </div>
                  <Link
                    href="/search"
                    onClick={() => setCategoriesOpen(false)}
                    className="mt-3 flex items-center justify-center gap-1 rounded-xl bg-purple-50 py-2 text-sm font-semibold text-purple-700 transition hover:bg-purple-100"
                  >
                    All Categories →
                  </Link>
                </div>
              </>
            )}
          </div>

          <Link href="/compare" className={`${navItemClass} ${pathname === "/compare" ? activeNavItemClass : ""}`}>
            <Scale className="h-4 w-4" /> Compare
          </Link>
          <Link href="/deals" className={`${navItemClass} ${pathname === "/deals" ? activeNavItemClass : ""}`}>
            <Tag className="h-4 w-4" /> Deals
          </Link>
          <Link href="/ai" className={`${navItemClass} ${pathname === "/ai" ? activeNavItemClass : ""}`}>
            <Sparkles className="h-4 w-4" /> AI Advisor
          </Link>
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <Link href="/search" className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:border-purple-300 hover:text-purple-600 lg:hidden">
            <Search className="h-4 w-4" />
          </Link>

          <Link href="/favorites" className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:border-pink-300 hover:text-pink-600">
            <Heart className="h-4 w-4" />
            {favoriteIds.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-pink-500 text-[10px] font-bold text-white">
                {favoriteIds.length}
              </span>
            )}
          </Link>

          <Link href="/ai" className="hidden rounded-xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-4 py-2 text-sm font-bold text-white transition hover:scale-[1.02] sm:flex">
            <Sparkles className="mr-1.5 h-4 w-4" /> Ask AI
          </Link>

          {!isLoading && (
            user ? (
              <div className="relative hidden lg:block">
                <button
                  onClick={() => setUserMenuOpen((o) => !o)}
                  className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition hover:border-purple-300"
                >
                  <User className="h-4 w-4" />
                  <span className="max-w-[100px] truncate">{user.full_name.split(" ")[0] || "Me"}</span>
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 top-12 z-50 min-w-[180px] rounded-2xl border border-gray-100 bg-white py-2 shadow-xl">
                    <Link href="/dashboard" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-purple-50 hover:text-purple-700">
                      <LayoutDashboard className="h-4 w-4" /> Dashboard
                    </Link>
                    <Link href="/notifications" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-purple-50 hover:text-purple-700">
                      <Bell className="h-4 w-4" /> Notifications
                    </Link>
                    <hr className="my-1 border-gray-100" />
                    <button onClick={() => { setUserMenuOpen(false); void logout(); }} className="flex w-full items-center gap-2 px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50">
                      <LogOut className="h-4 w-4" /> Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link href="/login" className="hidden items-center gap-1.5 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition hover:border-purple-300 hover:text-purple-700 lg:flex">
                <LogIn className="h-4 w-4" /> Sign In
              </Link>
            )
          )}

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen((o) => !o)}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 lg:hidden"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-gray-100 bg-white px-5 pb-4 lg:hidden">
          <nav className="mt-3 flex flex-col gap-1">
            {[
              { href: "/", label: "Home" },
              { href: "/search", label: "Browse Products" },
              { href: "/ai", label: "✨ AI Advisor" },
              { href: "/compare", label: "Compare" },
              { href: "/deals", label: "Deals" },
              { href: "/favorites", label: `Favorites (${favoriteIds.length})` },
            ].map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMobileOpen(false)}
                className="rounded-xl px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-purple-50 hover:text-purple-700"
              >
                {label}
              </Link>
            ))}
            <hr className="my-1 border-gray-100" />
            {user ? (
              <>
                <Link href="/dashboard" onClick={() => setMobileOpen(false)} className="rounded-xl px-4 py-3 text-sm font-semibold text-gray-700 hover:bg-purple-50 hover:text-purple-700">
                  Dashboard
                </Link>
                <button onClick={() => { setMobileOpen(false); void logout(); }} className="rounded-xl px-4 py-3 text-left text-sm font-semibold text-red-600 hover:bg-red-50">
                  Sign Out
                </button>
              </>
            ) : (
              <Link href="/login" onClick={() => setMobileOpen(false)} className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-3 text-center text-sm font-bold text-white">
                Sign In
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}