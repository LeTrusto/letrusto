import type { Metadata } from "next";

import FavoritesPage from "./FavoritesPage";

export const metadata: Metadata = {
  title: "Favorites",
  description: "Review the designs and products you have saved for later.",
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