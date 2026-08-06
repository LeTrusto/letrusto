"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Bell, Heart, LogIn, LogOut, Search, Sparkles, Scale, LayoutDashboard, Tag, User, Menu, X, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

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
  const [menusPath, setMenusPath] = useState(pathname);
  const categoriesRef = useRef<HTMLDivElement | null>(null);
  const userMenuRef = useRef<HTMLDivElement | null>(null);

  const isRouteCurrent = menusPath === pathname;
  const categoriesMenuVisible = categoriesOpen && isRouteCurrent;
  const userMenuVisible = userMenuOpen && isRouteCurrent;
  const mobileMenuVisible = mobileOpen && isRouteCurrent;

  const navItemClass =
    "inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[15px] font-semibold tracking-[0.01em] text-slate-700 transition hover:bg-slate-100 hover:text-slate-950";

  const activeNavItemClass = "bg-slate-100 text-slate-950 shadow-sm";

  const closeAllMenus = () => {
    setCategoriesOpen(false);
    setUserMenuOpen(false);
    setMobileOpen(false);
    setMenusPath(pathname);
  };

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node;

      if (categoriesRef.current && !categoriesRef.current.contains(target)) {
        setCategoriesOpen(false);
      }

      if (userMenuRef.current && !userMenuRef.current.contains(target)) {
        setUserMenuOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setCategoriesOpen(false);
        setUserMenuOpen(false);
        setMobileOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

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
        <nav className="hidden items-center gap-1 xl:flex">
          <Link href="/" onClick={closeAllMenus} className={navItemClass}>Home</Link>

          {/* Categories dropdown */}
          <div className="relative" ref={categoriesRef}>
            <button
              onClick={() => {
                setMenusPath(pathname);
                setCategoriesOpen((o) => !o);
              }}
              aria-expanded={categoriesMenuVisible}
              aria-haspopup="menu"
              aria-controls="desktop-categories-menu"
              className={`${navItemClass} gap-1`}
            >
              Categories
              <ChevronDown className={`h-3.5 w-3.5 transition ${categoriesMenuVisible ? "rotate-180" : ""}`} />
            </button>
            <AnimatePresence>
              {categoriesMenuVisible && (
                <motion.div
                  id="desktop-categories-menu"
                  role="menu"
                  initial={{ opacity: 0, y: 12, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.98 }}
                  transition={{ duration: 0.18, ease: "easeOut" }}
                  className="absolute left-0 top-12 z-50 w-[28rem] rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-[0_30px_90px_-40px_rgba(15,23,42,0.45)]"
                >
                  <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Browse by category</p>
                  <p className="mb-4 text-sm text-slate-500">Jump into product families and focused buying journeys.</p>
                  <div className="grid grid-cols-2 gap-2">
                    {CATALOG_TREE[0]?.children?.slice(0, 8).map((cat) => (
                      <Link
                        key={cat.slug}
                        href={`/category/${cat.slug}`}
                        onClick={() => setCategoriesOpen(false)}
                        role="menuitem"
                        className="flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 hover:text-slate-950"
                      >
                        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-base">{cat.icon}</span>
                        <span>{cat.name}</span>
                      </Link>
                    ))}
                  </div>
                  <Link
                    href="/categories"
                    onClick={() => setCategoriesOpen(false)}
                    className="mt-4 flex items-center justify-center gap-1 rounded-2xl bg-slate-950 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                  >
                    View all categories
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <Link href="/compare" onClick={closeAllMenus} className={`${navItemClass} ${pathname === "/compare" ? activeNavItemClass : ""}`}>
            <Scale className="h-4 w-4" /> Compare
          </Link>
          <Link href="/guides" onClick={closeAllMenus} className={`${navItemClass} ${pathname.startsWith("/articles") || pathname.startsWith("/guides") ? activeNavItemClass : ""}`}>
            📚 Guides
          </Link>
          <Link href="/deals" onClick={closeAllMenus} className={`${navItemClass} ${pathname === "/deals" ? activeNavItemClass : ""}`}>
            <Tag className="h-4 w-4" /> Deals
          </Link>
          <Link href="/ai" onClick={closeAllMenus} className={`${navItemClass} ${pathname === "/ai" ? activeNavItemClass : ""}`}>
            <Sparkles className="h-4 w-4" /> Buying Assistant
          </Link>
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <Link href="/search" onClick={closeAllMenus} className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:border-slate-300 hover:text-slate-900 xl:hidden" aria-label="Search products">
            <Search className="h-4 w-4" />
          </Link>

          <Link href="/favorites" onClick={closeAllMenus} className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:border-slate-300 hover:text-slate-900" aria-label="View favorites">
            <Heart className="h-4 w-4" />
            {favoriteIds.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-pink-500 text-[10px] font-bold text-white">
                {favoriteIds.length}
              </span>
            )}
          </Link>

          <Link href="/ai" onClick={closeAllMenus} className="hidden rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white transition hover:bg-slate-800 sm:flex">
            <Sparkles className="mr-1.5 h-4 w-4" /> Get Recommendations
          </Link>

          {!isLoading && (
            user ? (
              <div className="relative hidden xl:block" ref={userMenuRef}>
                <button
                  onClick={() => {
                    setMenusPath(pathname);
                    setUserMenuOpen((o) => !o);
                  }}
                  aria-expanded={userMenuVisible}
                  aria-haspopup="menu"
                  className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition hover:border-purple-300"
                >
                  <User className="h-4 w-4" />
                  <span className="max-w-[100px] truncate">{user.full_name.split(" ")[0] || "Me"}</span>
                </button>
                <AnimatePresence>
                  {userMenuVisible && (
                    <motion.div
                      role="menu"
                      initial={{ opacity: 0, y: 10, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.98 }}
                      transition={{ duration: 0.18, ease: "easeOut" }}
                      className="absolute right-0 top-12 z-50 min-w-[200px] rounded-2xl border border-gray-100 bg-white py-2 shadow-xl"
                    >
                      <Link href="/dashboard" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-slate-50 hover:text-slate-950">
                        <LayoutDashboard className="h-4 w-4" /> Dashboard
                      </Link>
                      <Link href="/notifications" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-slate-50 hover:text-slate-950">
                        <Bell className="h-4 w-4" /> Notifications
                      </Link>
                      <hr className="my-1 border-gray-100" />
                      <button onClick={() => { setUserMenuOpen(false); void logout(); }} className="flex w-full items-center gap-2 px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50">
                        <LogOut className="h-4 w-4" /> Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link href="/login" onClick={closeAllMenus} className="hidden items-center gap-1.5 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition hover:border-slate-300 hover:text-slate-950 xl:flex">
                <LogIn className="h-4 w-4" /> Sign In
              </Link>
            )
          )}

          {/* Mobile hamburger */}
          <button
            onClick={() => {
              setMenusPath(pathname);
              setMobileOpen((o) => !o);
            }}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 xl:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuVisible ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileMenuVisible && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="border-t border-gray-100 bg-white px-5 pb-4 xl:hidden"
          >
            <nav className="mt-3 flex flex-col gap-1">
              {[
                { href: "/", label: "Home" },
                { href: "/search", label: "Browse Products" },
                { href: "/ai", label: "✨ Buying Assistant" },
                { href: "/guides", label: "📚 Buying Guides" },
                { href: "/compare", label: "Compare" },
                { href: "/deals", label: "Deals" },
                { href: "/favorites", label: `Favorites (${favoriteIds.length})` },
              ].map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-xl px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-slate-50 hover:text-slate-950"
                >
                  {label}
                </Link>
              ))}
              <hr className="my-1 border-gray-100" />
              {user ? (
                <>
                  <Link href="/dashboard" onClick={() => setMobileOpen(false)} className="rounded-xl px-4 py-3 text-sm font-semibold text-gray-700 hover:bg-slate-50 hover:text-slate-950">
                    Dashboard
                  </Link>
                  <button onClick={() => { setMobileOpen(false); void logout(); }} className="rounded-xl px-4 py-3 text-left text-sm font-semibold text-red-600 hover:bg-red-50">
                    Sign Out
                  </button>
                </>
              ) : (
                <Link href="/login" onClick={() => setMobileOpen(false)} className="rounded-xl bg-slate-950 px-4 py-3 text-center text-sm font-bold text-white">
                  Sign In
                </Link>
              )}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}