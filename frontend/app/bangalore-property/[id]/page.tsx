"use client";

import Link from "next/link";
import Script from "next/script";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, LockKeyhole, Mail, MapPin, Phone } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import type { RazorpayResult } from "@/lib/razorpayCheckout";
import { getProperty, requestContactUnlock, verifyContactUnlock, type PropertyListing } from "@/services/property.service";

const TYPE_LABEL: Record<string, string> = { flat: "Flat", plot: "Plot", house: "House" };

function formatPrice(value: string): string {
	const amount = Number(value);
	if (!Number.isFinite(amount)) return value;
	if (amount >= 1_00_00_000) return `₹${(amount / 1_00_00_000).toFixed(2)} Cr`;
	if (amount >= 1_00_000) return `₹${(amount / 1_00_000).toFixed(2)} L`;
	return `₹${amount.toLocaleString("en-IN")}`;
}

export default function PropertyDetailPage() {
	const params = useParams<{ id: string }>();
	const { accessToken, isAuthenticated, user } = useAuth();
	const [listing, setListing] = useState<PropertyListing | null>(null);
	const [loading, setLoading] = useState(true);
	const [unlockState, setUnlockState] = useState<"idle" | "working" | "error">("idle");
	const [unlockError, setUnlockError] = useState("");

	useEffect(() => {
		let cancelled = false;
		getProperty(params.id, accessToken ?? undefined)
			.then((data) => !cancelled && setListing(data))
			.catch(() => !cancelled && setListing(null))
			.finally(() => !cancelled && setLoading(false));
		return () => {
			cancelled = true;
		};
	}, [params.id, accessToken]);

	async function unlockContact() {
		if (!accessToken || !listing) return;
		setUnlockState("working");
		setUnlockError("");
		try {
			const order = await requestContactUnlock(accessToken, listing.id);
			if (!window.Razorpay) throw new Error("Secure checkout is still loading. Please try again.");
			const checkout = new window.Razorpay({
				key: order.key_id,
				amount: order.amount,
				currency: order.currency,
				order_id: order.razorpay_order_id,
				name: "Bangalore Property",
				description: `Unlock contact — ${listing.title}`,
				prefill: { name: user?.full_name ?? "", email: user?.email ?? "", contact: "" },
				handler: async (result: RazorpayResult) => {
					try {
						const updated = await verifyContactUnlock(accessToken, listing.id, result);
						setListing(updated);
						setUnlockState("idle");
					} catch (error) {
						setUnlockState("error");
						setUnlockError(error instanceof Error ? error.message : "Payment verification failed.");
					}
				},
				modal: { ondismiss: () => setUnlockState("idle") },
			});
			checkout.on?.("payment.failed", (failure) => {
				setUnlockState("error");
				setUnlockError(failure.error?.description ?? "Payment failed.");
			});
			checkout.open();
		} catch (error) {
			setUnlockState("error");
			setUnlockError(error instanceof Error ? error.message : "Checkout could not be started.");
		}
	}

	if (loading) return <main className="p-10 text-center text-slate-500">Loading…</main>;
	if (!listing) return <main className="p-10 text-center text-slate-500">Listing not found.</main>;

	return (
		<main className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-orange-50 pb-16">
			<Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="afterInteractive" />
			<div className="mx-auto max-w-4xl px-4 py-8">
				<Link href="/bangalore-property" className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-700">
					<ArrowLeft size={16} /> Back to listings
				</Link>

				<div className="mt-6 overflow-hidden rounded-3xl border border-orange-100 bg-white shadow-lg">
					<div className="relative h-72 w-full bg-gradient-to-br from-orange-200 via-pink-200 to-sky-200">
						{listing.image_urls[0] ? (
							// eslint-disable-next-line @next/next/no-img-element
							<img src={listing.image_urls[0]} alt={listing.title} className="h-full w-full object-cover" />
						) : null}
						<span className="absolute left-4 top-4 rounded-full bg-black/70 px-3 py-1 text-xs font-bold uppercase text-white">
							{TYPE_LABEL[listing.property_type] ?? listing.property_type}
						</span>
					</div>

					<div className="p-6 sm:p-8">
						<p className="text-3xl font-black text-slate-900">{formatPrice(listing.price)}</p>
						<h1 className="mt-2 text-2xl font-bold text-slate-900">{listing.title}</h1>
						<p className="mt-1 flex items-center gap-1 text-sm text-slate-500">
							<MapPin size={14} /> {listing.locality}, {listing.city}
						</p>

						<div className="mt-4 flex flex-wrap gap-4 text-sm font-semibold text-slate-600">
							{listing.bedrooms != null && <span>{listing.bedrooms} BHK</span>}
							{listing.area_sqft && <span>{Number(listing.area_sqft).toLocaleString("en-IN")} sqft</span>}
						</div>

						<p className="mt-6 whitespace-pre-line text-slate-700">{listing.description}</p>

						<div className="mt-8 rounded-2xl border-2 border-dashed border-indigo-200 bg-indigo-50/50 p-6">
							{listing.contact_unlocked ? (
								<div className="space-y-2">
									<p className="text-sm font-bold uppercase tracking-wide text-indigo-700">Owner contact</p>
									<p className="flex items-center gap-2 text-slate-800"><Phone size={16} /> {listing.contact_phone}</p>
									{listing.contact_email && <p className="flex items-center gap-2 text-slate-800"><Mail size={16} /> {listing.contact_email}</p>}
									<p className="text-sm text-slate-600">{listing.contact_name}</p>
								</div>
							) : listing.is_own_listing ? (
								<p className="text-sm text-slate-600">This is your own listing — contact details are always visible to you on your dashboard.</p>
							) : !isAuthenticated ? (
								<div>
									<p className="flex items-center gap-2 text-sm font-bold text-slate-800"><LockKeyhole size={16} /> Sign in to unlock owner contact</p>
									<Link href={`/login?next=/bangalore-property/${listing.id}`} className="mt-3 inline-flex rounded-full bg-indigo-600 px-6 py-2 text-sm font-bold text-white">
										Sign in
									</Link>
								</div>
							) : (
								<div>
									<p className="flex items-center gap-2 text-sm font-bold text-slate-800"><LockKeyhole size={16} /> Contact details are locked</p>
									<p className="mt-1 text-sm text-slate-600">Pay a small unlock fee to see the owner&apos;s phone number and email directly.</p>
									{unlockError && <p className="mt-2 text-sm text-red-600">{unlockError}</p>}
									<button
										type="button"
										onClick={unlockContact}
										disabled={unlockState === "working"}
										className="mt-3 inline-flex rounded-full bg-indigo-600 px-6 py-2 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60"
									>
										{unlockState === "working" ? "Processing…" : "Unlock Contact Details"}
									</button>
								</div>
							)}
						</div>
					</div>
				</div>
			</div>
		</main>
	);
}
