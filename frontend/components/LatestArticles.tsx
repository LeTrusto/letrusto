import Link from "next/link";
import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type ArticleSummary = {
  slug: string;
  title: string;
  excerpt: string;
  category: string;
};

const CATEGORY_BADGES: Record<string, { label: string; class: string }> = {
  guide: { label: "Guide", class: "bg-blue-100 text-blue-700" },
  comparison: { label: "Comparison", class: "bg-purple-100 text-purple-700" },
  review: { label: "Review", class: "bg-amber-100 text-amber-700" },
};

async function getLatestArticles(): Promise<ArticleSummary[]> {
  if (!IS_API_CONFIGURED) return [];
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/articles?page_size=4`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const data = await res.json() as { items: ArticleSummary[] };
    return data.items;
  } catch {
    return [];
  }
}

export default async function LatestArticles() {
  const articles = await getLatestArticles();
  if (articles.length === 0) return null;

  return (
    <section className="py-12">
      <div className="mb-6 flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-black text-gray-900">Latest Buying Guides</h2>
          <p className="mt-1 text-sm text-gray-500">Expert research to help you decide before you buy</p>
        </div>
        <Link href="/articles" className="text-sm font-semibold text-purple-700 hover:underline">
          All guides →
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {articles.map((article) => {
          const badge = CATEGORY_BADGES[article.category] ?? CATEGORY_BADGES.guide;
          return (
            <Link
              key={article.slug}
              href={`/articles/${article.slug}`}
              className="group rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge.class}`}>
                {badge.label}
              </span>
              <h3 className="mt-2.5 text-base font-bold leading-snug text-gray-900 group-hover:text-purple-700">
                {article.title}
              </h3>
              <p className="mt-1 line-clamp-2 text-sm text-gray-500">{article.excerpt}</p>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
