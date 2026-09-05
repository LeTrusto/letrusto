"use client";

import Link from "next/link";
import { Suspense } from "react";
import { LayoutDashboard, LogOut, Menu, UserCircle } from "lucide-react";
import { usePathname } from "next/navigation";
import BrandMark from "./BrandMark";
import { useAuth } from "@/hooks/useAuth";

export default function CommerceNavbar() {
  return (
    <Suspense fallback={<NavbarFallback />}>
      <CommerceNavbarContent />
    </Suspense>
  );
}

function CommerceNavbarContent() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const links = [
    { href: "/#features", label: "Features" },
    { href: "/#pricing", label: "Pricing" },
    { href: "/#faq", label: "FAQ" },
  ];
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/95 text-white shadow-lg backdrop-blur-md">
      <div className="mx-auto flex min-h-[72px] max-w-7xl items-center justify-between gap-4 px-5 sm:px-8 lg:px-12">
        <BrandMark compact={false} tone="light" />
        <nav className="hidden items-center gap-1 text-sm font-semibold md:flex" aria-label="Primary navigation">
          {links.map(({ href, label }) => <Link key={href} href={href} className="rounded-lg px-3 py-2 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white">{label}</Link>)}
          {isAuthenticated && <Link href="/dashboard" className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 transition-colors ${pathname.startsWith("/dashboard") ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}><LayoutDashboard size={15} />Dashboard</Link>}
        </nav>
        <div className="flex items-center gap-2">
          {isAuthenticated ? <>
            <span className="hidden max-w-[180px] items-center gap-2 truncate rounded-lg border border-slate-700 bg-slate-800/70 px-3 py-2 text-sm font-semibold text-slate-200 sm:inline-flex" title={user?.full_name || user?.email || "Signed in"}><UserCircle size={16} className="shrink-0 text-slate-400" /> <span className="truncate">{user?.full_name || user?.email || "Signed in"}</span></span>
            <button type="button" onClick={() => void logout()} className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2.5 text-sm font-bold text-slate-300 transition-colors hover:border-slate-500 hover:text-white"><LogOut size={15} /> Sign Out</button>
          </> : <>
            <Link href="/login" className="hidden px-3 py-2 text-sm font-bold text-slate-300 transition-colors hover:text-white sm:inline">Sign In</Link>
            <Link href="/register" className="inline-flex items-center rounded-lg bg-[#2563eb] px-4 py-2.5 text-sm font-bold text-white shadow-[0_8px_20px_rgba(37,99,235,0.25)] transition-colors hover:bg-blue-500">Start Free</Link>
          </>}
          <span className="md:hidden" aria-hidden="true"><Menu size={20} className="text-slate-400" /></span>
        </div>
      </div>
    </header>
  );
}

function NavbarFallback() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/95 backdrop-blur-md">
      <div className="mx-auto flex min-h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8 lg:px-12"><BrandMark tone="light" /><Menu className="text-slate-400" aria-hidden="true" /></div>
    </header>
  );
}
