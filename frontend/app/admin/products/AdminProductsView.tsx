"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";
import { Calculator, ClipboardCheck } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Variant = {
  id: string;
  supplier_variant_id: string;
  supplier_variant_sku: string;
  name: string;
  attributes: string;
  supplier_cost: number | null;
  supplier_cost_usd: number | null;
  selling_price: number | null;
  total_inventory: number | null;
  cj_inventory: number | null;
  factory_inventory: number | null;
  verified_warehouse: string | null;
  weight_grams: number | null;
  active: boolean;
  position: number;
};

type Product = {
  id: string;
  name: string;
  description: string;
  status: "DRAFT" | "ACTIVE" | "PAUSED";
  commercial_status: "DRAFT" | "REVIEW" | "APPROVED" | "REJECTED";
  commercial_reasons: string[];
  commercial_reviewed_at: string | null;
  commercial_target_margin_percent: number | null;
  commercial_target_cac_inr: number | null;
  commercial_cac_supported: boolean | null;
  supplier_validation_status: "PASS" | "REVIEW" | "REJECT" | null;
  supplier_validation_score: number | null;
  supplier_validation_notes: string[];
  supplier_validated_at: string | null;
  market_price_status: "NOT_EVALUATED";
  supplier: string | null;
  supplier_product_id: string | null;
  supplier_cost: number | null;
  shipping_cost: number | null;
  selling_price: number | null;
  total_inventory: number | null;
  cj_inventory: number | null;
  factory_inventory: number | null;
  verified_warehouse: string | null;
  images: string[];
  variants: Variant[];
};

type ProductResponse = { products: Product[]; total: number };

type PricingInputs = {
  supplier_cost_usd: string;
  shipping_cost_usd: string;
  usd_to_inr_exchange_rate: string;
  platform_fee_percent: string;
  payment_fee_percent: string;
  rto_reserve_percent: string;
  target_margin_percent: string;
};

type PriceCalculation = {
  base_cost_inr: number;
  platform_fee_inr: number;
  payment_fee_inr: number;
  rto_reserve_inr: number;
  target_margin_percent: number;
  target_margin_inr: number;
  selling_price_inr: number;
  expected_profit_inr: number;
};

type VariantPriceCalculation = {
  variants: Array<{
    variant_id: string;
    supplier_variant_id: string;
    supplier_cost_usd: number;
    shipping_cost_inr: number;
    landed_cost_inr: number;
    selling_price_inr: number;
    payment_fee_inr: number;
    rto_reserve_inr: number;
    contribution_before_cac_inr: number;
    target_contribution_inr: number;
    max_cac_for_target_margin_inr: number;
    target_cac_inr: number;
    contribution_after_target_cac_inr: number;
    target_margin_status: "TARGET_MARGIN_MET" | "TARGET_MARGIN_NOT_MET";
    cac_target_status: "CAC_TARGET_SUPPORTED" | "CAC_TARGET_NOT_SUPPORTED";
    profitable_after_target_cac: boolean;
    unprofitable_after_target_cac: boolean;
  }>;
};

const emptyPricingInputs: PricingInputs = {
  supplier_cost_usd: "",
  shipping_cost_usd: "",
  usd_to_inr_exchange_rate: "",
  platform_fee_percent: "",
  payment_fee_percent: "",
  rto_reserve_percent: "",
  target_margin_percent: "",
};

const inrFormatter = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatInr(value: number) {
  return `₹${inrFormatter.format(value)}`;
}

async function apiError(response: Response): Promise<string> {
  const body = (await response.json().catch(() => null)) as { detail?: string | Array<{ msg: string }> } | null;
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) return body.detail.map((item) => item.msg).join("; ");
  return `API error ${response.status}`;
}

function apiHeaders(): Record<string, string> {
  const token = typeof window === "undefined" ? null : localStorage.getItem("lt_access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export default function AdminProductsView() {
  const [products, setProducts] = useState<Product[]>([]);
  const [supplierProductId, setSupplierProductId] = useState("");
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [syncingProductId, setSyncingProductId] = useState<string | null>(null);
  const [reviewingProductId, setReviewingProductId] = useState<string | null>(null);
  const [calculatingProductId, setCalculatingProductId] = useState<string | null>(null);
  const [pricingInputs, setPricingInputs] = useState<Record<string, PricingInputs>>({});
  const [priceCalculations, setPriceCalculations] = useState<Record<string, PriceCalculation | VariantPriceCalculation>>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products`, { headers: apiHeaders() });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const data = (await response.json()) as ProductResponse;
      setProducts(data.products.map((product) => ({
        ...product,
        commercial_status: product.commercial_status ?? "DRAFT",
        commercial_reasons: product.commercial_reasons ?? [],
        commercial_reviewed_at: product.commercial_reviewed_at ?? null,
        commercial_target_margin_percent: product.commercial_target_margin_percent ?? null,
        commercial_target_cac_inr: product.commercial_target_cac_inr ?? null,
        commercial_cac_supported: product.commercial_cac_supported ?? null,
        supplier_validation_status: product.supplier_validation_status ?? null,
        supplier_validation_score: product.supplier_validation_score ?? null,
        supplier_validation_notes: product.supplier_validation_notes ?? [],
        supplier_validated_at: product.supplier_validated_at ?? null,
        market_price_status: product.market_price_status ?? "NOT_EVALUATED",
      })));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load products");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(loadProducts);
  }, [loadProducts]);

  async function importProduct(event: React.FormEvent) {
    event.preventDefault();
    if (!supplierProductId.trim()) return;
    setWorking(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify({ supplier: "cj", supplier_product_id: supplierProductId.trim(), destination: "IN" }),
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      setMessage("Product imported as DRAFT.");
      setSupplierProductId("");
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import product");
    } finally {
      setWorking(false);
    }
  }

  async function updateStatus(product: Product, status: Product["status"]) {
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update status");
    }
  }

  async function syncInventory(product: Product) {
    setSyncingProductId(product.id);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/sync-inventory`, {
        method: "POST",
        headers: apiHeaders(),
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      setMessage(`Inventory synced for ${product.name}.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sync inventory");
    } finally {
      setSyncingProductId(null);
    }
  }

  async function runCommercialReview(product: Product) {
    setReviewingProductId(product.id);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/commercial-review`, {
        method: "POST",
        headers: apiHeaders(),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage(`Commercial review completed for ${product.name}.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run commercial review");
    } finally {
      setReviewingProductId(null);
    }
  }

  function updatePricingInput(productId: string, field: keyof PricingInputs, value: string) {
    setPricingInputs((current) => ({
      ...current,
      [productId]: { ...(current[productId] ?? emptyPricingInputs), [field]: value },
    }));
  }

  async function calculatePrice(event: React.FormEvent, product: Product) {
    event.preventDefault();
    setCalculatingProductId(product.id);
    setError("");
    setMessage("");
    try {
      const inputs = pricingInputs[product.id] ?? emptyPricingInputs;
      const usesVariantPricing = product.supplier_cost == null && product.variants.length > 0;
      const endpoint = usesVariantPricing ? "calculate-variant-prices" : "calculate-price";
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: usesVariantPricing ? undefined : JSON.stringify(inputs),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const calculation = (await response.json()) as PriceCalculation | VariantPriceCalculation;
      setPriceCalculations((current) => ({ ...current, [product.id]: calculation }));
      setMessage(`Price calculated for ${product.name}.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to calculate price");
    } finally {
      setCalculatingProductId(null);
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <div className="flex items-end justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold">Catalog Products</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Imported supplier products and catalog status.</p>
        </div>
        <span className="text-sm text-[var(--text-muted)]">{products.length} loaded</span>
      </div>

      <form onSubmit={(event) => void importProduct(event)} className="lt-card p-4 mb-6 flex flex-col sm:flex-row gap-3">
        <input
          value={supplierProductId}
          onChange={(event) => setSupplierProductId(event.target.value)}
          placeholder="CJ product ID"
          className="lt-input flex-1"
          aria-label="CJ product ID"
        />
        <button type="submit" disabled={working} className="lt-btn lt-btn-primary">
          {working ? "Importing..." : "Import as Draft"}
        </button>
      </form>

      {message && <p className="mb-4 text-sm text-green-700">{message}</p>}
      {error && <p className="mb-4 text-sm text-red-700">{error}</p>}

      {loading ? (
        <p className="text-sm text-[var(--text-muted)]">Loading catalog...</p>
      ) : products.length === 0 ? (
        <p className="text-sm text-[var(--text-muted)]">No imported products yet.</p>
      ) : (
        <div className="space-y-4">
          {products.map((product) => (
            <article key={product.id} className="lt-card p-4">
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                <div className="flex gap-4">
                  {product.images[0] && <Image src={product.images[0]} alt="" width={80} height={80} className="w-20 h-20 object-cover rounded-lg" />}
                  <div>
                    <h2 className="font-semibold">{product.name}</h2>
                    <p className="text-xs text-[var(--text-muted)] mt-1">CJ: {product.supplier_product_id ?? "-"}</p>
                    <p className="text-xs text-[var(--text-muted)]">Variants: {product.variants.length} · Images: {product.images.length}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button type="button" disabled={reviewingProductId !== null} onClick={() => void runCommercialReview(product)} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2">
                    <ClipboardCheck size={16} aria-hidden="true" />
                    {reviewingProductId === product.id ? "Reviewing..." : "Run Commercial Review"}
                  </button>
                  <button type="button" disabled={syncingProductId !== null} onClick={() => void syncInventory(product)} className="lt-btn lt-btn-secondary text-sm">
                    {syncingProductId === product.id ? "Syncing..." : "Sync Inventory"}
                  </button>
                  <select value={product.status} onChange={(event) => void updateStatus(product, event.target.value as Product["status"])} className="lt-select text-sm" aria-label={`Status for ${product.name}`}>
                    <option value="DRAFT">DRAFT</option>
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="PAUSED">PAUSED</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4 text-sm">
                <Metric label="Status" value={product.status} />
                <Metric label="CJ inventory" value={product.cj_inventory ?? 0} />
                <Metric label="Factory inventory" value={product.factory_inventory ?? 0} />
                <Metric label="Supplier cost (INR)" value={product.supplier_cost == null ? "-" : formatInr(product.supplier_cost)} />
                <Metric label="Shipping (INR)" value={product.shipping_cost == null ? "-" : formatInr(product.shipping_cost)} />
                <Metric label="Selling price" value={product.selling_price == null ? "-" : formatInr(product.selling_price)} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 border-t border-[var(--border)] pt-4 text-sm">
                <Metric label="Commercial status" value={product.commercial_status} />
                <Metric label="Target margin" value={product.commercial_target_margin_percent == null ? "-" : `${product.commercial_target_margin_percent}%`} />
                <Metric label="CAC target" value={product.commercial_target_cac_inr == null ? "-" : formatInr(product.commercial_target_cac_inr)} />
                <Metric label="CAC supported" value={product.commercial_cac_supported == null ? "NOT REVIEWED" : product.commercial_cac_supported ? "YES" : "NO"} />
                <Metric label="Market price" value={product.market_price_status} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4 border-t border-[var(--border)] pt-4 text-sm">
                <Metric label="Supplier validation" value={product.supplier_validation_status ?? "NOT AVAILABLE"} />
                <Metric label="Validation score" value={product.supplier_validation_score ?? "-"} />
                <Metric label="Validated" value={product.supplier_validated_at ? new Date(product.supplier_validated_at).toLocaleString("en-IN") : "-"} />
              </div>
              {(product.supplier_validation_notes ?? []).length > 0 && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">Validation issues: {(product.supplier_validation_notes ?? []).join(", ")}</p>
              )}
              {product.commercial_reasons.length > 0 && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">Reasons: {product.commercial_reasons.join(", ")}</p>
              )}
              <details className="mt-4 border-t border-[var(--border)] pt-4">
                <summary className="cursor-pointer text-sm font-semibold">Calculate Price</summary>
                <form onSubmit={(event) => void calculatePrice(event, product)} className="mt-3">
                  {product.supplier_cost != null && (
                    <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3">
                      <PriceInput label="Supplier USD" value={pricingInputs[product.id]?.supplier_cost_usd ?? ""} onChange={(value) => updatePricingInput(product.id, "supplier_cost_usd", value)} />
                      <PriceInput label="Shipping USD" value={pricingInputs[product.id]?.shipping_cost_usd ?? ""} onChange={(value) => updatePricingInput(product.id, "shipping_cost_usd", value)} />
                      <PriceInput label="USD to INR" value={pricingInputs[product.id]?.usd_to_inr_exchange_rate ?? ""} onChange={(value) => updatePricingInput(product.id, "usd_to_inr_exchange_rate", value)} />
                      <PriceInput label="Platform %" value={pricingInputs[product.id]?.platform_fee_percent ?? ""} onChange={(value) => updatePricingInput(product.id, "platform_fee_percent", value)} />
                      <PriceInput label="Payment %" value={pricingInputs[product.id]?.payment_fee_percent ?? ""} onChange={(value) => updatePricingInput(product.id, "payment_fee_percent", value)} />
                      <PriceInput label="RTO reserve %" value={pricingInputs[product.id]?.rto_reserve_percent ?? ""} onChange={(value) => updatePricingInput(product.id, "rto_reserve_percent", value)} />
                      <PriceInput label="Target margin %" value={pricingInputs[product.id]?.target_margin_percent ?? ""} onChange={(value) => updatePricingInput(product.id, "target_margin_percent", value)} />
                    </div>
                  )}
                  <button type="submit" disabled={calculatingProductId !== null} className="lt-btn lt-btn-primary text-sm mt-3 inline-flex items-center gap-2">
                    <Calculator size={16} aria-hidden="true" />
                    {calculatingProductId === product.id ? "Calculating..." : product.supplier_cost == null ? "Apply Launch Policy" : "Calculate Price"}
                  </button>
                </form>
                {priceCalculations[product.id] && !("variants" in priceCalculations[product.id]) && (
                  <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3 mt-4 text-sm">
                    <Metric label="Base cost" value={formatInr((priceCalculations[product.id] as PriceCalculation).base_cost_inr)} />
                    <Metric label="Platform fee" value={formatInr((priceCalculations[product.id] as PriceCalculation).platform_fee_inr)} />
                    <Metric label="Payment fee" value={formatInr((priceCalculations[product.id] as PriceCalculation).payment_fee_inr)} />
                    <Metric label="RTO reserve" value={formatInr((priceCalculations[product.id] as PriceCalculation).rto_reserve_inr)} />
                    <Metric label="Margin" value={`${(priceCalculations[product.id] as PriceCalculation).target_margin_percent}% (${formatInr((priceCalculations[product.id] as PriceCalculation).target_margin_inr)})`} />
                    <Metric label="Selling price" value={formatInr((priceCalculations[product.id] as PriceCalculation).selling_price_inr)} />
                    <Metric label="Expected profit" value={formatInr((priceCalculations[product.id] as PriceCalculation).expected_profit_inr)} />
                  </div>
                )}
                {priceCalculations[product.id] && "variants" in priceCalculations[product.id] && (
                  <div className="mt-4 overflow-x-auto">
                    <table className="w-full text-xs whitespace-nowrap">
                      <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2 pr-3">CJ VID</th><th className="pr-3">CJ cost USD</th><th className="pr-3">Shipping</th><th className="pr-3">Landed</th><th className="pr-3">Selling</th><th className="pr-3">Payment</th><th className="pr-3">RTO</th><th className="pr-3">Contribution before CAC</th><th className="pr-3">20% target</th><th className="pr-3">Max CAC</th><th className="pr-3">Target CAC</th><th className="pr-3">After CAC</th><th>Viability</th></tr></thead>
                      <tbody>{(priceCalculations[product.id] as VariantPriceCalculation).variants.map((variant) => (
                        <tr key={variant.variant_id} className="border-t border-[var(--border)] align-top">
                          <td className="py-2 pr-3">{variant.supplier_variant_id}</td>
                          <td className="pr-3">${variant.supplier_cost_usd}</td>
                          <td className="pr-3">{formatInr(variant.shipping_cost_inr)}</td>
                          <td className="pr-3">{formatInr(variant.landed_cost_inr)}</td>
                          <td className="pr-3 font-semibold">{formatInr(variant.selling_price_inr)}</td>
                          <td className="pr-3">{formatInr(variant.payment_fee_inr)}</td>
                          <td className="pr-3">{formatInr(variant.rto_reserve_inr)}</td>
                          <td className="pr-3">{formatInr(variant.contribution_before_cac_inr)}</td>
                          <td className="pr-3">{formatInr(variant.target_contribution_inr)}</td>
                          <td className="pr-3">{formatInr(variant.max_cac_for_target_margin_inr)}</td>
                          <td className="pr-3">{formatInr(variant.target_cac_inr)}</td>
                          <td className="pr-3">{formatInr(variant.contribution_after_target_cac_inr)}</td>
                          <td><span className="block">{variant.target_margin_status}</span><span className="block">{variant.cac_target_status}</span><span className="block">{variant.unprofitable_after_target_cac ? "UNPROFITABLE_AFTER_CAC" : "PROFITABLE_AFTER_CAC"}</span></td>
                        </tr>
                      ))}</tbody>
                    </table>
                  </div>
                )}
              </details>
              {product.variants.length > 0 && (
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2">CJ VID</th><th>SKU</th><th>Supplier USD</th><th>Supplier cost (INR)</th><th>Selling price</th><th>CJ inventory</th><th>Factory inventory</th></tr></thead>
                    <tbody>{product.variants.map((variant) => <tr key={variant.id} className="border-t border-[var(--border)]"><td className="py-2 pr-3">{variant.supplier_variant_id}</td><td className="pr-3">{variant.supplier_variant_sku}</td><td className="pr-3">{variant.supplier_cost_usd == null ? "-" : `$${variant.supplier_cost_usd}`}</td><td className="pr-3">{variant.supplier_cost == null ? "-" : formatInr(variant.supplier_cost)}</td><td className="pr-3">{variant.selling_price == null ? "-" : formatInr(variant.selling_price)}</td><td className="pr-3">{variant.cj_inventory ?? 0}</td><td>{variant.factory_inventory ?? 0}</td></tr>)}</tbody>
                  </table>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div><p className="text-[10px] uppercase text-[var(--text-muted)]">{label}</p><p className="font-semibold mt-1">{value}</p></div>;
}

function PriceInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="text-xs text-[var(--text-muted)]"><span>{label}</span><input type="number" min="0" step="any" required value={value} onChange={(event) => onChange(event.target.value)} className="lt-input w-full mt-1 text-sm" /></label>;
}
