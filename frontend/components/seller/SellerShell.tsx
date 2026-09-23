"use client";

import { ArrowLeft, LogOut, Plus, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/hooks/useAuth";
import NotificationCenter from "@/components/notifications/NotificationCenter";

export default function SellerShell({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading || !isAuthenticated) return <main className="seller-loading">Checking your session...</main>;

  return <div className="seller-app"><header className="seller-topbar"><Link href="/" className="seller-brand"><span className="mark-dot" />BENGALURU PROPERTY</Link><div className="seller-top-actions"><span className="seller-user-name">{user?.full_name || user?.email}</span><NotificationCenter /><button type="button" className="seller-icon-button" onClick={() => void logout()} aria-label="Sign out"><LogOut size={17} /></button></div></header><div className="seller-layout"><aside className="seller-sidebar"><p className="seller-kicker">Seller studio</p><nav aria-label="Seller navigation"><Link className={pathname === "/seller" ? "active" : ""} href="/seller">Your properties</Link><Link className={pathname.startsWith("/seller/leads") ? "active" : ""} href="/seller/leads">Buyer enquiries</Link><Link className={pathname === "/seller/profile" ? "active" : ""} href="/seller/profile"><UserRound size={16} /> Profile</Link></nav><Link href="/seller/properties/new" className="seller-add-link"><Plus size={17} /> Add property</Link><Link href="/properties" className="seller-back-link"><ArrowLeft size={15} /> Browse properties</Link></aside><main className="seller-main">{children}</main></div></div>;
}
