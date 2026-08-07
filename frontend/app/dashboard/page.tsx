import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Dashboard",
  description: "View your wishlist, saved comparisons, price alerts, and AI conversations.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/dashboard",
  },
};

export { default } from "./DashboardPage";
