"use client";

import Link from "next/link";
import Script from "next/script";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, LockKeyhole } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import type { RazorpayResult } from "@/lib/razorpayCheckout";
import { createProperty, verifyListingPayment, type PropertyListingCreatePayload, type PropertyType } from "@/services/property.service";

const EMPTY_FORM: PropertyListingCreatePayload = {
	property_type: "flat",
	title: "",
	description: "",
	locality: "",
	price: 0,
	area_sqft: undefined,
	bedrooms: undefined,
	image_urls: [],
	contact_name: "",
	contact_phone: "",
	contact_email: "",
};

export default function PostPropertyPage() {
	const { accessToken, isAuthenticated, user } = useAuth();
	const router = useRouter();
	const [form, setForm] = useState<PropertyListingCreatePayload>(EMPTY_FORM);
	const [imageUrlsText, setImageUrlsText] = useState("");
	const [state, setState] = useState<"idle" | "working" | "error" | "success">("idle");
	const [message, setMessage] = useState("");

	function update<K extends keyof PropertyListingCreatePayload>(key: K, value: PropertyListingCreatePayload[K]) {
		setForm((current) => ({ ...current, [key]: value }));
	}

	async function submitAndPay() {
		if (!accessToken) return;
		setState("working");
		setMessage("");
		try {
			const payload: PropertyListingCreatePayload = {
				...form,
				image_urls: imageUrlsText.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 12),
			};
			const order = await createProperty(accessToken, payload);
			if (!window.Razorpay) throw new Error("Secure checkout is still loading. Please try again.");
			const checkout = new window.Razorpay({
				key: order.key_id,
				amount: order.amount,
				currency: order.currency,
				order_id: order.razorpay_order_id,
				name: "Bangalore Property",
				description: "Listing fee",
				prefill: { name: user?.full_name ?? "", email: user?.email ?? "", contact: form.contact_phone },
				handler: async (result: RazorpayResult) => {
					try {
						await verifyListingPayment(accessToken, order.listing_id, result);
						setState("success");
						setMessage("Payment received. Your listing is submitted for review and will go live once approved.");
						window.setTimeout(() => router.push("/bangalore-property"), 2500);
					} catch (error) {
						setState("error");
						setMessage(error instanceof Error ? error.message : "Payment verification failed.");
					}
				},
				modal: { ondismiss: () => setState("idle") },
			});
			checkout.on?.("payment.failed", (failure) => {
				setState("error");
				setMessage(failure.error?.description ?? "Payment failed.");
			});
			checkout.open();
		} catch (error) {
			setState("error");
			setMessage(error instanceof Error ? error.message : "Listing could not be created.");
		}
	}

	if (!isAuthenticated) {
		return (
			<main className="mx-auto max-w-lg px-4 py-20 text-center">
				<p className="flex items-center justify-center gap-2 text-lg font-bold text-slate-800"><LockKeyhole size={18} /> Sign in to post a property</p>
				<Link href="/login?next=/bangalore-property/post" className="mt-6 inline-flex rounded-full bg-indigo-600 px-6 py-3 text-sm font-bold text-white">
					Sign in
				</Link>
			</main>
		);
	}

	return (
		<main className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-sky-50 pb-16">
			<Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="afterInteractive" />
			<div className="mx-auto max-w-2xl px-4 py-8">
				<Link href="/bangalore-property" className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-700">
					<ArrowLeft size={16} /> Back to listings
				</Link>
				<h1 className="mt-4 text-3xl font-black text-slate-900">Post Your Property</h1>
				<p className="mt-2 text-slate-600">List your flat, plot, or house in Bangalore. A small listing fee applies before your ad goes live.</p>

				{state === "success" ? (
					<div className="mt-8 rounded-2xl bg-emerald-50 p-6 text-emerald-800">{message}</div>
				) : (
					<form
						onSubmit={(event) => {
							event.preventDefault();
							void submitAndPay();
						}}
						className="mt-8 space-y-5 rounded-3xl border border-orange-100 bg-white p-6 shadow-sm sm:p-8"
					>
						<div className="grid grid-cols-3 gap-2">
							{(["flat", "plot", "house"] as PropertyType[]).map((type) => (
								<button
									key={type}
									type="button"
									onClick={() => update("property_type", type)}
									className={`rounded-xl px-4 py-3 text-sm font-bold capitalize transition ${
										form.property_type === type ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600"
									}`}
								>
									{type}
								</button>
							))}
						</div>

						<label className="block text-sm font-semibold text-slate-700">
							Title
							<input required maxLength={200} value={form.title} onChange={(event) => update("title", event.target.value)} placeholder="e.g. Spacious 3BHK near Whitefield" className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
						</label>

						<label className="block text-sm font-semibold text-slate-700">
							Description
							<textarea maxLength={4000} rows={4} value={form.description} onChange={(event) => update("description", event.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
						</label>

						<div className="grid grid-cols-2 gap-4">
							<label className="block text-sm font-semibold text-slate-700">
								Locality
								<input required maxLength={160} value={form.locality} onChange={(event) => update("locality", event.target.value)} placeholder="e.g. HSR Layout" className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
							<label className="block text-sm font-semibold text-slate-700">
								Price (₹)
								<input required type="number" min={1} value={form.price || ""} onChange={(event) => update("price", Number(event.target.value))} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
						</div>

						<div className="grid grid-cols-2 gap-4">
							<label className="block text-sm font-semibold text-slate-700">
								Area (sqft)
								<input type="number" min={1} value={form.area_sqft ?? ""} onChange={(event) => update("area_sqft", event.target.value ? Number(event.target.value) : undefined)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
							<label className="block text-sm font-semibold text-slate-700">
								Bedrooms
								<input type="number" min={0} max={20} value={form.bedrooms ?? ""} onChange={(event) => update("bedrooms", event.target.value ? Number(event.target.value) : undefined)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
						</div>

						<label className="block text-sm font-semibold text-slate-700">
							Photo URLs (one per line)
							<textarea rows={3} value={imageUrlsText} onChange={(event) => setImageUrlsText(event.target.value)} placeholder="https://…" className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
						</label>

						<div className="grid grid-cols-2 gap-4">
							<label className="block text-sm font-semibold text-slate-700">
								Your name
								<input required maxLength={200} value={form.contact_name} onChange={(event) => update("contact_name", event.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
							<label className="block text-sm font-semibold text-slate-700">
								Your phone
								<input required maxLength={20} value={form.contact_phone} onChange={(event) => update("contact_phone", event.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
							</label>
						</div>

						<label className="block text-sm font-semibold text-slate-700">
							Your email (optional)
							<input type="email" maxLength={255} value={form.contact_email ?? ""} onChange={(event) => update("contact_email", event.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5" />
						</label>

						{message && state === "error" && <p className="text-sm text-red-600">{message}</p>}

						<button type="submit" disabled={state === "working"} className="w-full rounded-full bg-indigo-600 px-6 py-3 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60">
							{state === "working" ? "Processing…" : "Pay Listing Fee & Submit"}
						</button>
					</form>
				)}
			</div>
		</main>
	);
}
