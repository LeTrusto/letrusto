"use client";

import { usePathname } from "next/navigation";

import CommerceFooter from "@/components/layout/CommerceFooter";
import CommerceNavbar from "@/components/layout/CommerceNavbar";
import MobileNav from "@/components/layout/MobileNav";

const AUTH_ROUTES = new Set([
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/verify-email",
]);

export default function CommerceShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthRoute = AUTH_ROUTES.has(pathname);

  return (
    <>
      {!isAuthRoute && <CommerceNavbar />}
      <main className={isAuthRoute ? "flex-1" : "flex-1 pb-16 lg:pb-0"}>{children}</main>
      {!isAuthRoute && <CommerceFooter />}
      {!isAuthRoute && <MobileNav />}
    </>
  );
}
