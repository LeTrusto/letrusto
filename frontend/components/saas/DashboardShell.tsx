"use client";

import { CreditCard, LogOut, MessageSquareQuote, PanelTop, Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import UpgradePlanModal from "@/components/saas/UpgradePlanModal";

const navItems = [
  { href: "/dashboard/widgets", label: "Widgets", icon: PanelTop },
  { href: "/dashboard/events", label: "Events", icon: MessageSquareQuote },
];

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const [upgradeOpen, setUpgradeOpen] = useState(false);

  if (isLoading) return <div className="flex min-h-[70vh] items-center justify-center bg-[#f3f7f5] text-sm text-[#587268]">Loading workspace...</div>;
  if (!isAuthenticated) {
    return <main className="flex min-h-[70vh] flex-col items-center justify-center bg-[#f3f7f5] px-6 text-center"><Sparkles className="h-10 w-10 text-[#e11d48]" /><h1 className="mt-5 text-2xl font-black text-[#17382e]">Your trust workspace is waiting</h1><p className="mt-2 max-w-md text-sm text-[#587268]">Sign in to manage widgets, publish social proof, and review your event stream.</p><Link href="/login?redirect=/dashboard/widgets" className="mt-6 bg-[#17382e] px-5 py-3 text-sm font-bold text-white hover:bg-[#0f2b23]">Sign in to continue</Link></main>;
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-[#f3f7f5] text-[#17382e]">
      <div className="mx-auto flex max-w-[1440px] flex-col lg:flex-row">
        <aside className="border-b border-[#d9e5df] bg-[#eef5f1] px-5 py-5 lg:min-h-[calc(100vh-80px)] lg:w-64 lg:border-b-0 lg:border-r lg:px-6 lg:py-8">
          <div className="flex items-center justify-between lg:block"><div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#e11d48]">LeTrusto / studio</p><h1 className="mt-2 text-xl font-black tracking-tight">Trust, in public.</h1></div><button type="button" onClick={() => void logout("/")} className="rounded-full p-2 text-[#71877f] hover:bg-white lg:mt-8" aria-label="Sign out"><LogOut className="h-4 w-4" /></button></div>
          <nav className="mt-7 flex gap-2 lg:flex-col" aria-label="Workspace navigation">
            {navItems.map(({ href, label, icon: Icon }) => <Link key={href} href={href} className={`flex items-center gap-3 px-3 py-2.5 text-sm font-bold transition ${pathname.startsWith(href) ? "bg-[#17382e] text-white" : "text-[#587268] hover:bg-white hover:text-[#17382e]"}`}><Icon className="h-4 w-4" />{label}</Link>)}
          </nav>
          <div className="mt-8 hidden border-t border-[#d9e5df] pt-6 lg:block"><p className="text-xs text-[#71877f]">Signed in as</p><p className="mt-1 truncate text-sm font-bold">{user?.full_name || user?.email}</p><button type="button" onClick={() => setUpgradeOpen(true)} className="mt-5 flex w-full items-center justify-center gap-2 bg-[#e11d48] px-3 py-2.5 text-xs font-bold text-white hover:bg-[#be123c]"><CreditCard className="h-4 w-4" /> Upgrade plan</button></div>
        </aside>
        <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12 lg:py-10">{children}</main>
      </div>
      <UpgradePlanModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} />
    </div>
  );
}
