import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import { notFound } from "next/navigation";
import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type Article = {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  category: string;
  meta_title: string | null;
  meta_description: string | null;
  view_count: number;
  created_at: string;
};

type Props = { params: Promise<{ slug: string }> };

async function getArticle(slug: string): Promise<Article | null> {
  if (!IS_API_CONFIGURED) return null;
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/articles/${slug}`, { next: { revalidate: 300 } });
    if (res.status === 404) return null;
    if (!res.ok) return null;
    return (await res.json()) as Article;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) return { title: "Article Not Found" };
  return {
    title: article.meta_title ?? article.title,
    description: article.meta_description ?? article.excerpt,
    openGraph: { title: article.title, description: article.excerpt, type: "article" },
    alternates: { canonical: `https://letrusto.com/articles/${slug}` },
  };
}

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) notFound();

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.excerpt,
    datePublished: article.created_at,
    publisher: { "@type": "Organization", name: "LeTrusto", url: "https://letrusto.com" },
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Script id="article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }} />

      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-2 text-sm text-gray-400">
        <Link href="/" className="hover:text-purple-700">Home</Link>
        <span>›</span>
        <Link href="/guides" className="hover:text-purple-700">Guides</Link>
        <span>›</span>
        <span className="text-gray-600">{article.title}</span>
      </nav>

      <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
        {article.category}
      </span>

      <h1 className="mt-4 text-4xl font-black leading-tight text-gray-900">{article.title}</h1>
      <p className="mt-3 text-lg text-gray-500">{article.excerpt}</p>

      <div className="mt-2 text-xs text-gray-400">
        {new Date(article.created_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" })}
        {" · "}
        {article.view_count} views
      </div>

      <hr className="my-8 border-gray-100" />

      {/* Article content — rendered as plain text with line breaks */}
      <div className="prose prose-gray max-w-none">
        {article.content.split("\n").map((para, i) =>
          para.trim() ? <p key={i} className="mb-4 leading-relaxed text-gray-700">{para}</p> : null
        )}
      </div>

      <hr className="my-10 border-gray-100" />

      <div className="rounded-2xl bg-gradient-to-r from-purple-50 to-pink-50 p-6">
        <h2 className="text-lg font-bold text-gray-900">Not sure which to buy?</h2>
        <p className="mt-1 text-sm text-gray-500">Ask our AI advisor and get a personalised recommendation in seconds.</p>
        <Link href={`/ai?q=${encodeURIComponent(article.title)}`} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-5 py-2.5 text-sm font-bold text-white">
          ✨ Ask AI Advisor
        </Link>
      </div>
    </main>
  );
}
