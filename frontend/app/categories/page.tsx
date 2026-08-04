import type { Metadata } from "next";
import Link from "next/link";

import { CATALOG_TREE } from "@/constants/index";

export const metadata: Metadata = {
  title: "Categories — LeTrusto",
  description: "Browse all LeTrusto product categories and jump directly to comparisons and recommendations.",
};

export default function CategoriesPage() {
  const allCategories = CATALOG_TREE.flatMap((group) => {
    if (!group.children || group.children.length === 0) {
      return [{ name: group.name, slug: group.slug, icon: group.icon }];
    }

    return group.children;
  });

  return (
    <main className="mx-auto max-w-7xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Categories</h1>
      <p className="mt-3 text-gray-500">Explore curated categories to find the right products faster.</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {allCategories.map((category) => (
          <Link
            key={category.slug}
            href={`/category/${category.slug}`}
            className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-purple-200 hover:shadow-md"
          >
            <p className="text-2xl">{category.icon}</p>
            <h2 className="mt-3 text-lg font-bold text-gray-900">{category.name}</h2>
            <p className="mt-1 text-sm text-gray-500">Browse recommendations and compare top picks.</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
