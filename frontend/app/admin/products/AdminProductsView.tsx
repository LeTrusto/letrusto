"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Variant = {
  id: string;
  supplier_variant_id: string;
  supplier_variant_sku: string;
  name: string;
  attributes: string;
  supplier_cost: number | null;
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

function apiHeaders(): Record<string, string> {
  const token = typeof window === "undefined" ? null : localStorage.getItem("lt_access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export default function AdminProductsView() {
  const [products, setProducts] = useState<Product[]>([]);
  const [includeLegacy, setIncludeLegacy] = useState(false);
  const [supplierProductId, setSupplierProductId] = useState("");
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const query = includeLegacy ? "?include_legacy=true" : "";
      const response = await fetch(`${API_BASE}/api/v1/admin/products${query}`, { headers: apiHeaders() });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const data = (await response.json()) as ProductResponse;
      setProducts(data.products);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load products");
    } finally {
      setLoading(false);
    }
  }, [includeLegacy]);

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

  return (
    <main className="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <div className="flex items-end justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold">Catalog Products</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Imported supplier products and catalog status.</p>
        </div>
        <span className="text-sm text-[var(--text-muted)]">{products.length} loaded</span>
      </div>

      <label className="flex items-center gap-2 mb-5 text-sm text-[var(--text-secondary)]">
        <input type="checkbox" checked={includeLegacy} onChange={(event) => setIncludeLegacy(event.target.checked)} />
        Legacy products
      </label>

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
                <select value={product.status} onChange={(event) => void updateStatus(product, event.target.value as Product["status"])} className="lt-select text-sm" aria-label={`Status for ${product.name}`}>
                  <option value="DRAFT">DRAFT</option>
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="PAUSED">PAUSED</option>
                </select>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 text-sm">
                <Metric label="Status" value={product.status} />
                <Metric label="CJ inventory" value={product.cj_inventory ?? 0} />
                <Metric label="Factory inventory" value={product.factory_inventory ?? 0} />
                <Metric label="Supplier cost" value={product.supplier_cost == null ? "-" : `₹${product.supplier_cost}`} />
                <Metric label="Selling price" value={product.selling_price == null ? "-" : `₹${product.selling_price}`} />
              </div>
              {product.variants.length > 0 && (
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2">CJ VID</th><th>SKU</th><th>CJ inventory</th><th>Factory inventory</th></tr></thead>
                    <tbody>{product.variants.map((variant) => <tr key={variant.id} className="border-t border-[var(--border)]"><td className="py-2 pr-3">{variant.supplier_variant_id}</td><td className="pr-3">{variant.supplier_variant_sku}</td><td className="pr-3">{variant.cj_inventory ?? 0}</td><td>{variant.factory_inventory ?? 0}</td></tr>)}</tbody>
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
