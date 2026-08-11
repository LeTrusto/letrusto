import type { Metadata } from "next";

import FavoritesPage from "./FavoritesPage";

export const metadata: Metadata = {
  title: "Favorites",
  description: "Review AI tools and software you have saved for comparison.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/favorites",
  },
};

export default function Page() {
  return <FavoritesPage />;
}