import type { Metadata } from "next";

import FavoritesPage from "./FavoritesPage";

export const metadata: Metadata = {
  title: "Favorites",
  description: "Review products you have saved for later comparison and shopping.",
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