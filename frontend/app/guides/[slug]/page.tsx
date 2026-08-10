import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type Props = {
  params: Promise<{ slug: string }>;
};

type Article = {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  category: string;
  content?: string;
  created_at: string;
  updated_at?: string;
};

async function getArticle(slug: string): Promise<Article | null> {
  if (!IS_API_CONFIGURED) return null;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/articles/${slug}`, {
      signal: controller.signal,
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return (await res.json()) as Article;
  } catch {
    return null;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) {
    return {
      title: "Guide Not Found",
      description: "The requested buying guide could not be found.",
    };
  }

  return {
    title: article.title,
    description: article.excerpt,
    alternates: { canonical: `/guides/${article.slug}` },
    openGraph: {
      title: article.title,
      description: article.excerpt,
      url: `/guides/${article.slug}`,
      siteName: "LeTrusto",
      type: "article",
      images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      title: article.title,
      description: article.excerpt,
      images: ["/images/og-default.svg"],
    },
  };
}

export default async function GuideDetailPage({ params }: Props) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) {
    notFound();
  }

  const publishedDate = new Date(article.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const updatedDate = article.updated_at
    ? new Date(article.updated_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null;

  const CATEGORY_LABELS: Record<string, string> = {
    guide: "Buying Guide",
    comparison: "Comparison",
    review: "Brand Review",
    deals: "Deals",
  };

  const categoryLabel = CATEGORY_LABELS[article.category] ?? article.category;

  return (
    <main className="min-h-screen bg-white px-6 py-12">
      <div className="mx-auto max-w-3xl">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6 text-xs text-slate-500">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="hover:text-slate-700">Home</Link></li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li><Link href="/guides" className="hover:text-slate-700">Guides</Link></li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li className="font-medium text-slate-700" aria-current="page">{article.title}</li>
          </ol>
        </nav>

        {/* Header */}
        <header className="mb-8">
          <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
            {categoryLabel}
          </span>
          <h1 className="mt-4 text-4xl font-black tracking-tight text-slate-950">
            {article.title}
          </h1>
          <p className="mt-3 text-lg leading-relaxed text-slate-600">{article.excerpt}</p>
          <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span>Published {publishedDate}</span>
            {updatedDate && updatedDate !== publishedDate ? (
              <span>Updated {updatedDate}</span>
            ) : null}
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600">
              Verified by LeTrusto research
            </span>
          </div>

          {/* Affiliate disclosure for guide pages */}
          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
            <strong className="font-semibold text-slate-700">Affiliate disclosure:</strong>{" "}
            This guide may contain affiliate links. LeTrusto may earn a commission when you
            purchase through qualifying links at no extra cost to you.{" "}
            <Link
              href="/affiliate-disclosure"
              className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
            >
              Learn more
            </Link>
          </div>
        </header>

        {/* Content — rendered if available */}
        {article.content ? (
          <article
            className="prose prose-slate max-w-none"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-200 py-16 text-center">
            <p className="text-3xl">📚</p>
            <h2 className="mt-4 text-xl font-bold text-slate-900">
              Full guide coming soon
            </h2>
            <p className="mt-2 text-slate-500">
              Our research team is preparing the full content for this guide.
            </p>
            <Link
              href="/ai"
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white"
            >
              ✨ Ask our AI instead
            </Link>
          </div>
        )}

        {/* Footer nav */}
        <div className="mt-10 flex flex-wrap items-center gap-4 border-t border-slate-100 pt-8">
          <Link
            href="/guides"
            className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500"
          >
            ← All guides
          </Link>
          <Link
            href="/ai-tools"
            className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500"
          >
            Browse AI tools
          </Link>
          <Link
            href="/methodology"
            className="text-xs text-slate-400 underline underline-offset-2 hover:text-slate-600"
          >
            How we research
          </Link>
        </div>
      </div>
    </main>
  );
}
