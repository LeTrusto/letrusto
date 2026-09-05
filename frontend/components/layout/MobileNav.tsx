"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, LayoutDashboard, Sparkles, Tag } from "lucide-react";
import clsx from "clsx";
import { useAuth } from "@/hooks/useAuth";

const TABS = [
  { label: "Home", href: "/", icon: Home },
  { label: "Features", href: "/#features", icon: Sparkles },
  { label: "Pricing", href: "/#pricing", icon: Tag },
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
] as const;

export default function MobileNav() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();
  const visibleTabs = isAuthenticated ? TABS : TABS.slice(0, 3);

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-[var(--border)] bg-[var(--surface)] safe-area-pb lg:hidden" aria-label="Mobile navigation">
      <div className="flex h-[68px] items-center justify-around px-1">
        {visibleTabs.map((tab) => {
          const isActive = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href.split("?")[0]);
          const Icon = tab.icon;
          return (
            <Link
              key={tab.label}
              href={tab.href}
              className={clsx(
                "flex h-full w-full flex-col items-center justify-center gap-1 text-[10px] font-medium transition-colors",
                isActive ? "text-[var(--lt-primary)]" : "text-[var(--text-muted)]"
              )}
            >
              <Icon size={20} strokeWidth={isActive ? 2 : 1.5} />
              <span>{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
