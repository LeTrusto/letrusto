import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Dashboard",
  description: "View your saved products, account details, and orders.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/dashboard",
  },
};

export { default } from "./DashboardPage";
