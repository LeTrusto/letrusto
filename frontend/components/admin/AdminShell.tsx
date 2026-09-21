"use client";

import { ClipboardList, LayoutDashboard, LogOut, UsersRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

export default function AdminShell({ children }: { children: React.ReactNode }) {
  const { user, isAdmin, isAuthenticated, isLoading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  useEffect(() => { if (!isLoading && !isAuthenticated) router.replace(`/login?redirect=${encodeURIComponent(pathname)}`); }, [isAuthenticated, isLoading, pathname, router]);
  if (isLoading || !isAuthenticated) return <main className="admin-loading">Checking your session...</main>;
  if (!isAdmin) return <main className="admin-loading"><h1>Admin access required</h1><p>This account is not authorized for operations.</p><Link href="/">Return to the public site</Link></main>;
  const nav = [{ href: "/admin", label: "Overview", icon: LayoutDashboard }, { href: "/admin/properties", label: "Properties", icon: ClipboardList }, { href: "/admin/enquiries", label: "Enquiries", icon: ClipboardList }, { href: "/admin/sellers", label: "Sellers", icon: UsersRound }];
  return <div className="admin-app"><header className="admin-topbar"><Link href="/admin" className="admin-brand"><span className="mark-dot" />BENGALURU PROPERTY <small>OPERATIONS</small></Link><div className="admin-user"><span>{user?.full_name || user?.email}</span><button type="button" onClick={() => void logout()} aria-label="Sign out"><LogOut size={16} /></button></div></header><div className="admin-layout"><aside className="admin-sidebar"><p className="admin-eyebrow">Control room</p><nav aria-label="Admin navigation">{nav.map(({ href, label, icon: Icon }) => <Link key={href} className={pathname === href || (href !== "/admin" && pathname.startsWith(href)) ? "active" : ""} href={href}><Icon size={16} />{label}</Link>)}</nav></aside><main className="admin-main">{children}</main></div></div>;
}
