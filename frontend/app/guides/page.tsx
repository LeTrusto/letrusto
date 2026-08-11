import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";

import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type Article = {
	id: number;
	slug: string;
	title: string;
	excerpt: string;
	category: string;
	created_at: string;
};

const AI_GUIDE_KEYWORDS = [
	"ai",
	"tool",
	"assistant",
	"software",
	"saas",
	"automation",
	"writing",
	"design",
	"video",
	"audio",
	"coding",
	"developer",
	"workflow",
	"productivity",
];

function isAiGuide(article: Article): boolean {
	const haystack = `${article.title} ${article.excerpt} ${article.slug} ${article.category}`.toLowerCase();
	return AI_GUIDE_KEYWORDS.some((keyword) => haystack.includes(keyword));
}

export const metadata: Metadata = {
	title: "Buying Guides",
	description:
		"Expert buying guides, software comparisons, and honest reviews to help you choose the right AI tools.",
	alternates: {
		canonical: "/guides",
	},
	openGraph: {
		title: "Buying Guides",
		description:
			"Expert buying guides, software comparisons, and honest reviews to help you choose the right AI tools.",
		url: "/guides",
		siteName: "LeTrusto",
		type: "website",
		images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
	},
	twitter: {
		card: "summary_large_image",
		title: "Buying Guides",
		description:
			"Expert buying guides, software comparisons, and honest reviews to help you choose the right AI tools.",
		images: ["/images/og-default.svg"],
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
	const articles = (await getArticles()).filter(isAiGuide);

	const GUIDE_CATEGORIES = [
		{ label: "AI Assistants", slug: "best-ai-assistants", description: "Compare general-purpose AI assistants for productivity, research, and writing." },
		{ label: "AI Writing Tools", slug: "best-ai-writing-tools", description: "Find the right AI writing tool for content, copywriting, and marketing." },
		{ label: "AI Coding Tools", slug: "best-ai-coding-tools", description: "Developer-focused AI tools for code generation, review, and debugging." },
		{ label: "AI Video Tools", slug: "best-ai-video-tools", description: "Tools for AI video generation, editing, and content creation." },
		{ label: "AI Image & Design", slug: "best-ai-image-tools", description: "AI image generators and design tools for creators and marketers." },
		{ label: "AI Voice & Audio", slug: "best-ai-voice-tools", description: "Voice synthesis, transcription, and audio AI tools." },
	];

	const PUBLISHED_GUIDES = [
		{ slug: "/guides/elevenlabs-pricing", title: "ElevenLabs Pricing: Which Plan Is Right for You?", category: "Pricing Guide", tool: "ElevenLabs" },
		{ slug: "/guides/elevenlabs-vs-murf-ai", title: "ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?", category: "Comparison", tool: "ElevenLabs" },
		{ slug: "/guides/highlevel-pricing", title: "HighLevel Pricing: Plans, Features & What You Should Know", category: "Pricing Guide", tool: "HighLevel" },
		{ slug: "/guides/moosend-pricing", title: "Moosend Pricing: Plans, Features & Who It Is For", category: "Pricing Guide", tool: "Moosend" },
		{ slug: "/guides/beehiiv-pricing", title: "beehiiv Pricing: Plans, Features & Newsletter Costs", category: "Pricing Guide", tool: "beehiiv" },
		{ slug: "/guides/synthesia-pricing", title: "Synthesia Pricing: Plans, Features & AI Video Costs", category: "Pricing Guide", tool: "Synthesia" },
		{ slug: "/guides/beehiiv-vs-substack", title: "beehiiv vs Substack: Which Newsletter Platform Is Right for You?", category: "Comparison", tool: "beehiiv" },
	];

	return (
		<main className="mx-auto max-w-4xl px-6 py-12">
			<SchemaOrg
				type="WebPage"
				data={{
					name: "Buying Guides",
					url: "https://letrusto.com/guides",
					description: "Expert buying guides, software comparisons, and honest reviews to help you choose the right AI tools.",
				}}
			/>
			<div className="mb-10">
				<p className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Research & Comparison</p>
				<h1 className="mt-3 text-4xl font-black text-gray-900">AI Tools Buying Guides</h1>
				<p className="mt-3 text-lg text-gray-500">
					Research-backed guides to help you choose the right software before you pay.
					Each guide explains what a tool does, who it is for, and where its trade-offs appear.
				</p>
			</div>

			{/* Published guides */}
			<section className="mb-10">
				<h2 className="mb-4 text-sm font-bold uppercase tracking-widest text-gray-500">Published Guides</h2>
				<div className="space-y-3">
					{PUBLISHED_GUIDES.map((guide) => (
						<Link
							key={guide.slug}
							href={guide.slug}
							className="group block rounded-[var(--radius-xl)] border border-[var(--border)] bg-white p-5 transition hover:border-[var(--lt-purple-light)] hover:shadow-[var(--shadow-md)]"
						>
							<div className="flex items-center gap-2 mb-1.5">
								<span className="lt-badge lt-badge-brand">{guide.category}</span>
								<span className="text-xs text-[var(--text-muted)]">{guide.tool}</span>
							</div>
							<h3 className="text-lg font-bold text-[var(--text-primary)] group-hover:text-[var(--lt-purple)]">{guide.title}</h3>
						</Link>
					))}
				</div>
			</section>

			{/* Guide categories — always visible to establish the content structure */}
			<section className="mb-10">
				<h2 className="mb-4 text-sm font-bold uppercase tracking-widest text-gray-500">Guide Topics</h2>
				<div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
					{GUIDE_CATEGORIES.map((cat) => (
						<div
							key={cat.slug}
							className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm"
						>
							<h3 className="font-bold text-gray-900">{cat.label}</h3>
							<p className="mt-1 text-xs leading-relaxed text-gray-500">{cat.description}</p>
							<p className="mt-3 text-xs font-medium text-purple-600">In preparation</p>
						</div>
					))}
				</div>
			</section>

			{articles.length === 0 ? (
				<div className="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
					<p className="text-4xl">📚</p>
					<h2 className="mt-4 text-xl font-bold text-gray-900">Guides in progress</h2>
					<p className="mt-2 text-gray-500">
						Our research team is preparing detailed buying guides. Check back soon — or ask our AI for immediate guidance.
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
							href={`/guides/${article.slug}`}
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

			<div className="mt-10 flex flex-wrap items-center gap-4 border-t border-gray-100 pt-8">
				<Link href="/ai-tools" className="rounded-xl border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:border-gray-500">
					Browse AI tools
				</Link>
				<Link href="/compare" className="rounded-xl border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:border-gray-500">
					Compare tools
				</Link>
				<Link href="/methodology" className="text-xs text-gray-400 underline underline-offset-2 hover:text-gray-600">
					How we research
				</Link>
			</div>
		</main>
	);
}
