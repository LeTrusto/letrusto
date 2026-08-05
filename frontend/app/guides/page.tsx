import type { Metadata } from "next";
import Link from "next/link";

import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type Article = {
	id: number;
	slug: string;
	title: string;
	excerpt: string;
	category: string;
	created_at: string;
};

export const metadata: Metadata = {
	title: "Buying Guides and Reviews",
	description:
		"Expert buying guides, product comparisons, and honest reviews to help you make better purchase decisions.",
	alternates: {
		canonical: "/guides",
	},
};

const CATEGORY_LABELS: Record<string, string> = {
	guide: "Buying Guide",
	comparison: "Comparison",
	review: "Brand Review",
	deals: "Deals",
};

async function getArticles(): Promise<Article[]> {
	if (!IS_API_CONFIGURED) return [];

	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), 4000);

	try {
		const res = await fetch(`${API_BASE_URL}/api/v1/articles?page_size=20`, {
			signal: controller.signal,
			next: { revalidate: 300 },
		});

		if (!res.ok) return [];
		const data = (await res.json()) as { items: Article[] };
		return data.items;
	} catch {
		return [];
	} finally {
		clearTimeout(timeoutId);
	}
}

export default async function GuidesPage() {
	const articles = await getArticles();

	return (
		<main className="mx-auto max-w-4xl px-6 py-12">
			<div className="mb-10">
				<h1 className="text-4xl font-black text-gray-900">Buying Guides and Reviews</h1>
				<p className="mt-3 text-lg text-gray-500">Expert guides to help you decide before you buy.</p>
			</div>

			{articles.length === 0 ? (
				<div className="rounded-2xl border border-dashed border-gray-200 py-20 text-center">
					<p className="text-4xl">📚</p>
					<h2 className="mt-4 text-xl font-bold text-gray-900">Coming soon</h2>
					<p className="mt-2 text-gray-500">
						Our editorial team is writing detailed buying guides. Check back soon!
					</p>
					<Link
						href="/ai"
						className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white"
					>
						✨ Ask our AI instead
					</Link>
				</div>
			) : (
				<div className="space-y-6">
					{articles.map((article) => (
						<Link
							key={article.slug}
							href={`/articles/${article.slug}`}
							className="group block rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
						>
							<div className="mb-2 flex items-center gap-2">
								<span className="rounded-full bg-purple-100 px-3 py-0.5 text-xs font-semibold text-purple-700">
									{CATEGORY_LABELS[article.category] ?? article.category}
								</span>
								<span className="text-xs text-gray-400">
									{new Date(article.created_at).toLocaleDateString()}
								</span>
							</div>
							<h2 className="text-xl font-bold text-gray-900 group-hover:text-purple-700">{article.title}</h2>
							<p className="mt-2 text-sm text-gray-500">{article.excerpt}</p>
						</Link>
					))}
				</div>
			)}
		</main>
	);
}
