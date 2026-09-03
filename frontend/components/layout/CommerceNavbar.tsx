"use client";

import Link from "next/link";
import { Suspense } from "react";
import { BriefcaseBusiness, FileText, Home, LayoutGrid, Menu, Sparkles, User, Wrench } from "lucide-react";
import { usePathname } from "next/navigation";
import BrandMark from "./BrandMark";

export default function CommerceNavbar() {
  return (
    <Suspense fallback={<NavbarFallback />}>
      <CommerceNavbarContent />
    </Suspense>
  );
}

function CommerceNavbarContent() {
  const pathname = usePathname();
  const links = [
    { href: "/", label: "Home", icon: Home },
    { href: "/tools", label: "Tools", icon: Wrench },
    { href: "/digital-products", label: "Digital Products", icon: FileText },
    { href: "/services", label: "Services", icon: BriefcaseBusiness },
    { href: "/minku-dinku", label: "Minku & Dinku", icon: Sparkles },
    { href: "/about", label: "About", icon: LayoutGrid },
  ];
  return (
    <header className="sticky top-0 z-50 bg-[var(--background)] shadow-[0_4px_18px_rgba(60,35,100,0.06)]">
      <div className="flex min-h-[76px] items-center justify-between gap-3 px-4 lg:hidden">
        <BrandMark compact />
      </div>
      <div className="mx-auto hidden min-h-[92px] max-w-[1280px] items-center justify-between px-6 lg:flex">
        <div className="flex min-w-0 items-center gap-8">
          <BrandMark />
          <nav className="flex items-center gap-1 text-sm font-semibold" aria-label="Primary navigation">
            {links.map(({ href, label, icon: Icon }) => {
              const active = href === "/" ? pathname === href : pathname.startsWith(href);
              return <Link key={href} href={href} aria-current={active ? "page" : undefined} className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 transition-colors ${active ? "bg-[var(--lt-primary)]/10 text-[var(--lt-primary)]" : "text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]"}`}><Icon size={15} strokeWidth={2} />{label}</Link>;
            })}
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/account" className="inline-flex h-11 items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-sm font-bold text-[var(--text-primary)] transition-colors hover:border-[var(--lt-accent)] hover:text-[var(--lt-primary)]" aria-label="Account">
            <User size={18} strokeWidth={2} /> <span>Account</span>
          </Link>
        </div>
      </div>
    </header>
  );
}

function NavbarFallback() {
  return (
    <header className="sticky top-0 z-50 bg-[var(--background)] shadow-[0_4px_18px_rgba(60,35,100,0.06)]">
      <div className="flex min-h-[76px] items-center justify-between px-4 lg:hidden"><BrandMark compact /><Menu className="text-[var(--lt-primary)]" aria-hidden="true" /></div>
      <div className="mx-auto hidden min-h-[92px] max-w-[1280px] items-center px-6 lg:flex"><BrandMark /></div>
    </header>
  );
}
