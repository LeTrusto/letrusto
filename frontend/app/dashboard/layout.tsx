import type { Metadata } from "next";

import DashboardShell from "@/components/saas/DashboardShell";

export const metadata: Metadata = {
  title: "Trust Studio",
  description: "Manage LeTrusto social proof widgets and customer events.",
  robots: { index: false, follow: false },
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>;
}
