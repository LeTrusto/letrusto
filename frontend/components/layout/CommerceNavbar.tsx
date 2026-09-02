"use client";

import Link from "next/link";
import { Suspense } from "react";
import { User } from "lucide-react";
import BrandMark from "./BrandMark";

export default function CommerceNavbar() {
  return (
    <Suspense fallback={<NavbarFallback />}>
      <CommerceNavbarContent />
    </Suspense>
  );
}

function CommerceNavbarContent() {
  return (
    <header className="sticky top-0 z-50 bg-[var(--background)] shadow-[0_4px_18px_rgba(60,35,100,0.06)]">
      <div className="flex min-h-[76px] items-center justify-between gap-3 px-4 lg:hidden">
        <BrandMark compact />
      </div>
      <div className="mx-auto hidden min-h-[92px] max-w-[1280px] items-center justify-between px-6 lg:flex">
        <div className="flex min-w-0 items-center gap-8">
          <BrandMark />
          <nav className="flex items-center gap-1 text-sm font-semibold" aria-label="Primary navigation">
            <Link href="/" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">Home</Link>
            <Link href="/tools" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">Tools</Link>
            <Link href="/digital-products" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">Digital Products</Link>
            <Link href="/services" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">Services</Link>
            <Link href="/minku-dinku" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">Minku &amp; Dinku</Link>
            <Link href="/about" className="rounded-md px-3 py-2 text-[var(--text-secondary)] hover:bg-[var(--lt-purple)]/10 hover:text-[var(--text-primary)]">About</Link>
          </nav>
        </div>
        <div className="flex items-center gap-2">
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
    <header className="sticky top-0 z-50 bg-[var(--background)] shadow-[0_4px_18px_rgba(60,35,100,0.06)]">
      <div className="flex min-h-[76px] items-center justify-between px-4 lg:hidden"><BrandMark compact /></div>
      <div className="mx-auto hidden min-h-[92px] max-w-[1280px] items-center px-6 lg:flex"><BrandMark /></div>
    </header>
  );
}
