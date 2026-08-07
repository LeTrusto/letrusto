import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Notifications",
  description: "View your price drop alerts, wishlist updates, and deal notifications.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/notifications",
  },
};

export { default } from "./NotificationsPage";
