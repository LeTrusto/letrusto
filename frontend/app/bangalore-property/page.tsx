"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Building2, Home, LandPlot, MapPin, Search } from "lucide-react";
import { listProperties, type PropertyListing, type PropertyType } from "@/services/property.service";

const TYPE_ICON: Record<PropertyType, typeof Home> = { flat: Building2, plot: LandPlot, house: Home };
const TYPE_LABEL: Record<PropertyType, string> = { flat: "Flat", plot: "Plot", house: "House" };

function formatPrice(value: string): string {
	const amount = Number(value);
	if (!Number.isFinite(amount)) return value;
	if (amount >= 1_00_00_000) return `₹${(amount / 1_00_00_000).toFixed(2)} Cr`;
	if (amount >= 1_00_000) return `₹${(amount / 1_00_000).toFixed(2)} L`;
	return `₹${amount.toLocaleString("en-IN")}`;
}

function PropertyCard({ listing }: { listing: PropertyListing }) {
	const Icon = TYPE_ICON[listing.property_type];
	const cover = listing.image_urls[0];
	return (
		<Link
			href={`/bangalore-property/${listing.id}`}
			className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/40 bg-white shadow-md transition hover:-translate-y-1 hover:shadow-xl"
		>
			<div className="relative h-44 w-full overflow-hidden bg-gradient-to-br from-orange-200 via-pink-200 to-sky-200">
				{cover ? (
					// eslint-disable-next-line @next/next/no-img-element
					<img src={cover} alt={listing.title} className="h-full w-full object-cover transition group-hover:scale-105" />
				) : (
					<div className="flex h-full w-full items-center justify-center text-orange-500/60"><Icon size={48} /></div>
				)}
				<span className="absolute left-3 top-3 rounded-full bg-black/70 px-3 py-1 text-xs font-bold uppercase tracking-wide text-white">
					{TYPE_LABEL[listing.property_type]}
				</span>
				{listing.is_featured && (
					<span className="absolute right-3 top-3 rounded-full bg-gradient-to-r from-amber-400 to-orange-500 px-3 py-1 text-xs font-bold text-white shadow">
						★ Featured
					</span>
				)}
			</div>
			<div className="flex flex-1 flex-col gap-2 p-4">
				<p className="text-lg font-black text-slate-900">{formatPrice(listing.price)}</p>
				<p className="line-clamp-1 text-sm font-semibold text-slate-700">{listing.title}</p>
				<p className="flex items-center gap-1 text-xs text-slate-500"><MapPin size={13} /> {listing.locality}, {listing.city}</p>
				<div className="mt-auto flex items-center gap-3 pt-2 text-xs font-medium text-slate-500">
					{listing.bedrooms != null && <span>{listing.bedrooms} BHK</span>}
					{listing.area_sqft && <span>{Number(listing.area_sqft).toLocaleString("en-IN")} sqft</span>}
				</div>
			</div>
		</Link>
	);
}

export default function BangalorePropertyPage() {
	const [items, setItems] = useState<PropertyListing[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [propertyType, setPropertyType] = useState<PropertyType | "">("");
	const [locality, setLocality] = useState("");
	const [heroIndex, setHeroIndex] = useState(0);

	const featured = useMemo(() => items.filter((item) => item.is_featured).slice(0, 5), [items]);
	const heroSlides = featured.length ? featured : items.slice(0, 5);

	useEffect(() => {
		if (heroSlides.length < 2) return;
		const timer = window.setInterval(() => setHeroIndex((current) => (current + 1) % heroSlides.length), 4000);
		return () => window.clearInterval(timer);
	}, [heroSlides.length]);

	useEffect(() => {
		let cancelled = false;
		void Promise.resolve().then(async () => {
			setLoading(true);
			setError("");
			try {
				const page = await listProperties({ property_type: propertyType || undefined, locality: locality || undefined, page: 1, page_size: 24 });
				if (cancelled) return;
				setItems(page.items);
				setTotal(page.total);
			} catch {
				if (!cancelled) setError("Listings could not be loaded. Please try again.");
			} finally {
				if (!cancelled) setLoading(false);
			}
		});
		return () => {
			cancelled = true;
		};
	}, [propertyType, locality]);

	return (
		<main className="min-h-screen bg-gradient-to-b from-sky-50 via-orange-50 to-white">
			<section className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 py-16 text-white">
				<div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.15),transparent_40%)]" />
				<div className="mx-auto max-w-6xl px-4">
					<p className="text-sm font-bold uppercase tracking-widest text-white/80">Bangalore Property</p>
					<h1 className="mt-2 max-w-2xl text-4xl font-black leading-tight sm:text-5xl">
						Flats, Plots &amp; Houses in Bangalore — Verified, Direct, Simple.
					</h1>
					<p className="mt-4 max-w-xl text-white/90">
						Browse real listings across Bangalore. Unlock direct owner contact instantly — no agent runaround.
					</p>
					<div className="mt-8 flex flex-wrap gap-3">
						<Link href="/bangalore-property/post" className="rounded-full bg-white px-6 py-3 text-sm font-bold text-indigo-700 shadow-lg transition hover:scale-105">
							Post Your Property
						</Link>
						<a href="#listings" className="rounded-full border-2 border-white/70 px-6 py-3 text-sm font-bold text-white transition hover:bg-white/10">
							Browse Listings
						</a>
					</div>
				</div>

				{heroSlides.length > 0 && (
					<div className="relative mx-auto mt-10 max-w-6xl px-4">
						<div className="overflow-hidden rounded-2xl border border-white/30 bg-white/10 backdrop-blur">
							<div className="flex transition-transform duration-700" style={{ transform: `translateX(-${heroIndex * 100}%)` }}>
								{heroSlides.map((slide) => (
									<Link
										key={slide.id}
										href={`/bangalore-property/${slide.id}`}
										className="flex min-w-full items-center justify-between gap-6 p-6 sm:p-8"
									>
										<div>
											<p className="text-xs font-bold uppercase tracking-wide text-white/70">{TYPE_LABEL[slide.property_type]} · {slide.locality}</p>
											<p className="mt-1 text-2xl font-black">{slide.title}</p>
											<p className="mt-2 text-3xl font-black text-amber-300">{formatPrice(slide.price)}</p>
										</div>
										{slide.image_urls[0] && (
											// eslint-disable-next-line @next/next/no-img-element
											<img src={slide.image_urls[0]} alt={slide.title} className="h-28 w-40 rounded-xl object-cover shadow-lg" />
										)}
									</Link>
								))}
							</div>
						</div>
						<div className="mt-3 flex justify-center gap-2">
							{heroSlides.map((slide, index) => (
								<button
									key={slide.id}
									type="button"
									aria-label={`Show slide ${index + 1}`}
									onClick={() => setHeroIndex(index)}
									className={`h-2 w-6 rounded-full transition ${index === heroIndex ? "bg-white" : "bg-white/40"}`}
								/>
							))}
						</div>
					</div>
				)}
			</section>

			<section id="listings" className="mx-auto max-w-6xl px-4 py-10">
				<div className="flex flex-wrap items-center gap-3 rounded-2xl border border-orange-100 bg-white p-4 shadow-sm">
					<div className="flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2">
						<Search size={16} className="text-slate-400" />
						<input
							value={locality}
							onChange={(event) => setLocality(event.target.value)}
							placeholder="Search by locality (e.g. Whitefield, HSR Layout)"
							className="w-64 bg-transparent text-sm outline-none"
						/>
					</div>
					{(["", "flat", "plot", "house"] as const).map((type) => (
						<button
							key={type || "all"}
							type="button"
							onClick={() => setPropertyType(type as PropertyType | "")}
							className={`rounded-full px-4 py-2 text-sm font-bold transition ${
								propertyType === type ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
							}`}
						>
							{type ? TYPE_LABEL[type as PropertyType] : "All"}
						</button>
					))}
					<span className="ml-auto text-sm font-medium text-slate-500">{total} listing{total === 1 ? "" : "s"}</span>
				</div>

				{error && <p className="mt-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}
				{loading ? (
					<p className="mt-10 text-center text-slate-500">Loading listings…</p>
				) : items.length === 0 ? (
					<p className="mt-10 text-center text-slate-500">No listings match yet — be the first to post one.</p>
				) : (
					<div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
						{items.map((listing) => (
							<PropertyCard key={listing.id} listing={listing} />
						))}
					</div>
				)}
			</section>
		</main>
	);
}
