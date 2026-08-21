"use client";

import { useState } from "react";
import { Lock, Play } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { runFulfillmentPreflight, type FulfillmentPreflight } from "@/services/fulfillmentPreflight.service";

type PreflightProduct = {
	id: string;
	name: string;
	variants: Array<{ id: string; name: string; supplier_variant_id: string }>;
};

export default function FulfillmentPreflightPanel({ products }: { products: PreflightProduct[] }) {
	const { accessToken, isLoading, isAuthenticated, isAdmin } = useAuth();
	const [productId, setProductId] = useState("");
	const [variantId, setVariantId] = useState("");
	const [quantity, setQuantity] = useState("1");
	const [destination, setDestination] = useState("IN");
	const [logisticsName, setLogisticsName] = useState("");
	const [storageId, setStorageId] = useState("");
	const [result, setResult] = useState<FulfillmentPreflight | null>(null);
	const [error, setError] = useState("");
	const [working, setWorking] = useState(false);

	const effectiveProductId = productId || products[0]?.id || "";
	const selectedProduct = products.find((product) => product.id === effectiveProductId);
	const effectiveVariantId = selectedProduct?.variants.some((variant) => variant.id === variantId)
		? variantId
		: selectedProduct?.variants[0]?.id || "";

	async function handleSubmit(event: React.FormEvent) {
		event.preventDefault();
		if (!accessToken || !effectiveProductId || !effectiveVariantId) return;
		setWorking(true);
		setError("");
		setResult(null);
		try {
			setResult(await runFulfillmentPreflight(accessToken, {
				productId: effectiveProductId,
				variantId: effectiveVariantId,
				quantity: Number(quantity),
				destination: destination.trim().toUpperCase(),
				logisticsName: logisticsName.trim() || undefined,
				storageId: storageId.trim() || undefined,
			}));
		} catch (requestError) {
			setError(requestError instanceof Error ? requestError.message : "Preflight request failed");
		} finally {
			setWorking(false);
		}
	}

	if (isLoading) return null;
	if (!isAuthenticated || !isAdmin) return null;

	return (
		<section className="mb-6 border-y border-[var(--border)] py-5">
			<div className="flex items-start gap-3">
				<Lock size={18} aria-hidden="true" />
				<div><h2 className="text-lg font-semibold">Fulfillment preflight</h2><p className="text-sm text-[var(--text-muted)] mt-1">Read-only warehouse and freight validation for an active catalog variant.</p></div>
			</div>
			<form onSubmit={(event) => void handleSubmit(event)} className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
				<label className="text-xs text-[var(--text-muted)]"><span>Product</span><select aria-label="Preflight product" className="lt-select mt-1 w-full" value={effectiveProductId} onChange={(event) => { setProductId(event.target.value); setVariantId(""); setResult(null); }}><option value="">Select product</option>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select></label>
				<label className="text-xs text-[var(--text-muted)]"><span>Variant</span><select aria-label="Preflight variant" className="lt-select mt-1 w-full" value={effectiveVariantId} onChange={(event) => { setVariantId(event.target.value); setResult(null); }} disabled={!selectedProduct}><option value="">Select variant</option>{selectedProduct?.variants.map((variant) => <option key={variant.id} value={variant.id}>{variant.name || variant.supplier_variant_id} · {variant.supplier_variant_id}</option>)}</select></label>
				<label className="text-xs text-[var(--text-muted)]"><span>Quantity</span><input aria-label="Preflight quantity" className="lt-input mt-1 w-full" min="1" required type="number" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label>
				<label className="text-xs text-[var(--text-muted)]"><span>Destination</span><input aria-label="Preflight destination" className="lt-input mt-1 w-full uppercase" maxLength={2} minLength={2} required value={destination} onChange={(event) => setDestination(event.target.value.toUpperCase())} /></label>
				<label className="text-xs text-[var(--text-muted)]"><span>Logistics name (optional)</span><input aria-label="Preflight logistics name" className="lt-input mt-1 w-full" placeholder="Any carrier" value={logisticsName} onChange={(event) => setLogisticsName(event.target.value)} /></label>
				<label className="text-xs text-[var(--text-muted)]"><span>Storage ID (optional)</span><input aria-label="Preflight storage ID" className="lt-input mt-1 w-full" placeholder="Any warehouse" value={storageId} onChange={(event) => setStorageId(event.target.value)} /></label>
				<button type="submit" disabled={working || !accessToken || !effectiveProductId || !effectiveVariantId} className="lt-btn lt-btn-primary mt-1 w-fit"><Play size={15} aria-hidden="true" />{working ? "Checking..." : "Run preflight"}</button>
			</form>
			{error && <p role="alert" className="mt-4 border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
			{result && <PreflightResult result={result} />}
		</section>
	);
}

function PreflightResult({ result }: { result: FulfillmentPreflight }) {
		return <section aria-live="polite" className={`mt-5 border p-4 ${result.fulfillable ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}`}><h3 className="font-bold">{result.fulfillable ? "FULFILLABLE" : "NOT_FULFILLABLE"}</h3>{result.reason && <p className="mt-1 text-sm">Reason: {result.reason}</p>}<dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4"><Fact label="Warehouse" value={result.warehouse_name} /><Fact label="Storage ID" value={result.warehouse_id} /><Fact label="Country" value={result.origin_country} /><Fact label="Sellable inventory" value={result.sellable_inventory} /><Fact label="Logistics name" value={result.logistic_name} /><Fact label="Freight cost" value={result.shipping_cost == null ? null : `$${result.shipping_cost.toFixed(2)}`} /><Fact label="Delivery estimate" value={result.delivery_estimate} /></dl></section>;
}

function Fact({ label, value }: { label: string; value: string | number | null }) { return <div><dt className="text-[10px] uppercase text-[var(--text-muted)]">{label}</dt><dd className="mt-1 font-semibold">{value ?? "—"}</dd></div>; }