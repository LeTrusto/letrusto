"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Bell, Heart, LogIn, LogOut, Search, Sparkles, Scale, LayoutDashboard, User, Menu, X, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useFavorites } from "@/hooks/useFavorites";
import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";

function isActive(pathname: string, href: string, prefixes?: string[]): boolean {
  if (href === "/") return pathname === "/";
  if (pathname === href) return true;
  return prefixes ? prefixes.some((p) => pathname.startsWith(p)) : pathname.startsWith(href);
}

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

  const navItemBase =
    "inline-flex items-center gap-2 rounded-[var(--radius-lg)] px-4 py-2.5 text-[0.9375rem] font-semibold text-slate-600 transition-colors duration-150 hover:text-[var(--lt-purple)] hover:bg-[var(--lt-gradient-soft)]";
  const navItemActive =
    "bg-[rgba(124,58,237,0.08)] text-[var(--lt-purple)]";

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

  const aiToolsActive = isActive(pathname, "/ai-tools", ["/ai-tools", "/category/"]);

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/95 shadow-[var(--shadow-sm)] backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-5 px-5 py-3.5 sm:px-6">
        {/* Logo */}
        <Link href="/" aria-label="LeTrusto home" className="flex shrink-0 items-center">
          <Image src="/LeTrusto%20Brand%20Logo.png" alt="LeTrusto - Discover. Choose. Trust." width={1774} height={887} priority unoptimized className="h-auto w-40 sm:w-44" />
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-0.5 xl:flex">
          <Link href="/" onClick={closeAllMenus} className={`${navItemBase} ${isActive(pathname, "/") ? navItemActive : ""}`}>Home</Link>

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
              className={`${navItemBase} gap-1.5 ${aiToolsActive ? navItemActive : ""}`}
            >
              AI Tools
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
                  className="absolute left-0 top-14 z-50 w-[28rem] rounded-[var(--radius-2xl)] border border-[var(--border)] bg-white p-5 shadow-[0_30px_90px_-40px_rgba(15,23,42,0.35)]"
                >
                  <p className="lt-label mb-1">Browse AI tool categories</p>
                  <p className="mb-4 text-sm text-slate-500">Find the right tool category before committing budget.</p>
                  <div className="grid grid-cols-2 gap-2">
                    {AI_TOOLS_PUBLIC_CATEGORIES.map((cat) => (
                      <Link
                        key={cat.id}
                        href={cat.href}
                        onClick={() => setCategoriesOpen(false)}
                        role="menuitem"
                        className="flex items-center gap-3 rounded-[var(--radius-lg)] px-3 py-3 text-sm font-medium text-slate-700 transition hover:bg-[var(--lt-gradient-soft)] hover:text-[var(--lt-purple)]"
                      >
                        <span className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-slate-100 text-base">{cat.icon}</span>
                        <span>{cat.name}</span>
                      </Link>
                    ))}
                  </div>
                  <Link
                    href="/ai-tools"
                    onClick={() => setCategoriesOpen(false)}
                    className="lt-btn lt-btn-md lt-btn-primary mt-4 w-full justify-center"
                  >
                    View all AI tool categories
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <Link href="/compare" onClick={closeAllMenus} className={`${navItemBase} ${isActive(pathname, "/compare") ? navItemActive : ""}`}>
            <Scale className="h-4 w-4" /> Compare
          </Link>
          <Link href="/guides" onClick={closeAllMenus} className={`${navItemBase} ${isActive(pathname, "/guides", ["/guides", "/articles"]) ? navItemActive : ""}`}>
            Guides
          </Link>
          <Link href="/about" onClick={closeAllMenus} className={`${navItemBase} ${isActive(pathname, "/about") ? navItemActive : ""}`}>
            About
          </Link>
          <Link href="/ai" onClick={closeAllMenus} className={`${navItemBase} ${isActive(pathname, "/ai") ? navItemActive : ""}`}>
            <Sparkles className="h-4 w-4" /> Ask AI
          </Link>
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2.5">
          <Link href="/search" onClick={closeAllMenus} className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border)] text-slate-500 transition hover:border-[var(--lt-purple-light)] hover:text-[var(--lt-purple)] xl:hidden" aria-label="Search AI tools">
            <Search className="h-[1.125rem] w-[1.125rem]" />
          </Link>

          <Link href="/favorites" onClick={closeAllMenus} className="relative flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border)] text-slate-500 transition hover:border-[var(--lt-purple-light)] hover:text-[var(--lt-purple)]" aria-label="View favorites">
            <Heart className="h-[1.125rem] w-[1.125rem]" />
            {favoriteIds.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-[1.125rem] w-[1.125rem] items-center justify-center rounded-full bg-[var(--lt-pink)] text-[10px] font-bold text-white">
                {favoriteIds.length}
              </span>
            )}
          </Link>

          <Link href="/ai" onClick={closeAllMenus} className="lt-btn lt-btn-md lt-btn-brand hidden sm:inline-flex">
            <Sparkles className="h-4 w-4" /> Ask LeTrusto
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
                  className="lt-btn lt-btn-md lt-btn-secondary"
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
                      className="absolute right-0 top-14 z-50 min-w-[220px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-white py-2 shadow-[var(--shadow-md)]"
                    >
                      <Link href="/dashboard" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2.5 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-[var(--lt-gradient-soft)] hover:text-[var(--lt-purple)]">
                        <LayoutDashboard className="h-4 w-4" /> Dashboard
                      </Link>
                      <Link href="/notifications" onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2.5 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-[var(--lt-gradient-soft)] hover:text-[var(--lt-purple)]">
                        <Bell className="h-4 w-4" /> Notifications
                      </Link>
                      <hr className="my-1.5 border-[var(--border)]" />
                      <button onClick={() => { setUserMenuOpen(false); void logout(); }} className="flex w-full items-center gap-2.5 px-4 py-3 text-sm font-medium text-red-600 transition hover:bg-red-50">
                        <LogOut className="h-4 w-4" /> Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link href="/login" onClick={closeAllMenus} className="lt-btn lt-btn-md lt-btn-secondary hidden xl:inline-flex">
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
            className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border)] text-slate-500 xl:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuVisible ? <X className="h-[1.125rem] w-[1.125rem]" /> : <Menu className="h-[1.125rem] w-[1.125rem]" />}
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
            className="border-t border-[var(--border)] bg-white px-5 pb-5 xl:hidden"
          >
            <nav className="mt-3 flex flex-col gap-0.5">
              {[
                { href: "/", label: "Home" },
                { href: "/ai-tools", label: "AI Tools" },
                { href: "/search", label: "Search" },
                { href: "/ai", label: "Ask AI" },
                { href: "/guides", label: "Buying Guides" },
                { href: "/compare", label: "Compare" },
                { href: "/about", label: "About" },
                { href: "/favorites", label: `Favorites (${favoriteIds.length})` },
              ].map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className={`rounded-[var(--radius-lg)] px-4 py-3.5 text-[0.9375rem] font-semibold transition ${
                    isActive(pathname, href, href === "/guides" ? ["/guides", "/articles"] : undefined)
                      ? "bg-[rgba(124,58,237,0.08)] text-[var(--lt-purple)]"
                      : "text-slate-600 hover:bg-[var(--lt-gradient-soft)] hover:text-[var(--lt-purple)]"
                  }`}
                >
                  {label}
                </Link>
              ))}
              <hr className="my-2 border-[var(--border)]" />
              {user ? (
                <>
                  <Link href="/dashboard" onClick={() => setMobileOpen(false)} className="rounded-[var(--radius-lg)] px-4 py-3.5 text-[0.9375rem] font-semibold text-slate-600 transition hover:bg-[var(--lt-gradient-soft)] hover:text-[var(--lt-purple)]">
                    Dashboard
                  </Link>
                  <button onClick={() => { setMobileOpen(false); void logout(); }} className="rounded-[var(--radius-lg)] px-4 py-3.5 text-left text-[0.9375rem] font-semibold text-red-600 transition hover:bg-red-50">
                    Sign Out
                  </button>
                </>
              ) : (
                <Link href="/login" onClick={() => setMobileOpen(false)} className="lt-btn lt-btn-md lt-btn-primary w-full justify-center">
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