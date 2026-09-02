"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Wrench, BriefcaseBusiness, Package, UserCircle } from "lucide-react";
import clsx from "clsx";

const TABS = [
  { label: "Home", href: "/", icon: Home },
  { label: "Tools", href: "/tools", icon: Wrench },
  { label: "Services", href: "/services", icon: BriefcaseBusiness },
  { label: "Orders", href: "/dashboard", icon: Package },
  { label: "Account", href: "/account", icon: UserCircle },
] as const;

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-[var(--border)] bg-[var(--surface)] safe-area-pb lg:hidden" aria-label="Mobile navigation">
      <div className="flex items-center justify-around h-16">
        {TABS.map((tab) => {
          const isActive = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href.split("?")[0]);
          const Icon = tab.icon;
          return (
            <Link
              key={tab.label}
              href={tab.href}
              className={clsx(
                "flex flex-col items-center justify-center gap-0.5 w-full h-full text-[10px] font-medium transition-colors",
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
