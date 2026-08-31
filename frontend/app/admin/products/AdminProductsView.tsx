"use client";

import { Fragment, useCallback, useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Calculator, Check, CirclePause, ClipboardCheck, ExternalLink, Play, RefreshCw, Trash2, X } from "lucide-react";
import { API_BASE_URL } from "@/services/api";
import FulfillmentPreflightPanel from "./FulfillmentPreflightPanel";

const API_BASE = API_BASE_URL;
const LEGACY_CJ_WORKFLOW_ENABLED = false;

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
  approval_decided_at: string | null;
  approval_decided_by_user_id: string | null;
  approval_rejection_reason: string | null;
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
  supplier_validation_details: Record<string, unknown> | null;
  variants: Variant[];
};

type ProductResponse = { products: Product[]; total: number };

type PrintfulConnection = { connected: boolean; store: string | null; status: string; message: string | null };
type PrintfulProduct = { supplier_product_id: string; name: string; thumbnail_url: string | null; finalized: boolean; imported_product_id: string | null };
type PrintfulProductsResponse = { products: PrintfulProduct[]; total: number };
type LegacyArchiveResponse = { supplier: "cj"; archived_count: number; status: string };

type FulfillmentOrder = {
  order_id: string;
  order_number: string;
  payment_status: string;
  total: number;
  fulfillment_status: string;
  supplier_order_id: string | null;
  failure_reason: string | null;
  customer_email: string;
  tracking_number: string | null;
  tracking_carrier: string | null;
  supplier_status: string | null;
  last_supplier_sync_at: string | null;
};

type SupplierCandidate = {
  id: string;
  supplier: "cj";
  supplier_product_id: string;
  supplier_sku: string | null;
  name: string;
  approval_status: "REVIEW" | "APPROVED" | "REJECTED" | "IMPORTED";
  readiness_status: "DISCOVERED" | "VALIDATED" | "REJECTED" | "REVIEW";
  supplier_validation_status: "PASS" | "REVIEW" | "REJECT" | null;
  supplier_validation_score: number | null;
  commercial_status: "REVIEW" | "APPROVED" | "REJECTED";
  market_status: "NOT_EVALUATED" | "INSUFFICIENT_MARKET_DATA" | "MARKET_EVIDENCE_AVAILABLE" | "MARKET_COMPETITIVE" | "MARKET_ABOVE_OBSERVED";
  discovery_min_selling_price_inr: number | null;
  discovery_max_selling_price_inr: number | null;
  snapshot_status: "AVAILABLE" | "LEGACY_SNAPSHOT_UNAVAILABLE";
  main_image: string | null;
  images: string[];
  warehouses: Array<{ supplier_variant_id?: string; warehouse_country?: string; storage_id?: string | null; warehouse_name?: string | null; total_inventory?: number; cj_inventory?: number; factory_inventory?: number; verification_status?: string | null }>;
  logistics: { available?: boolean; validation?: string | null; origin_country?: string | null; destination_country?: string | null; selected?: { carrier?: string; method?: string; cost_usd?: number; estimated_days?: string } | null };
  freight: { available?: boolean; cost_usd?: number | null; cost_inr?: number | string | null; delivery_estimate?: string | null };
  commercial_result: { minimum_price_inr?: number | string | null; maximum_price_inr?: number | string | null; target_margin_percent?: number | string | null; cac_viable?: boolean | null; failure_reasons?: string[] };
  failure_reasons: string[];
  validation_issues: string[];
  target_margin_percent: number | null;
  target_cac_inr: number | null;
  cac_viable: boolean | null;
  variants: Array<{
    supplier_variant_id: string;
    supplier_variant_sku: string;
    name: string;
    attributes: string;
    supplier_cost_usd: number | null;
    supplier_cost_inr: number | null;
    weight_grams: number | null;
    total_inventory: number | null;
    cj_inventory: number | null;
    factory_inventory: number | null;
    selling_price_inr: number | null;
    target_margin_status: string | null;
    cac_target_status: string | null;
  }>;
  market_evidence_count: number;
  approved_at: string | null;
  imported_product_id: string | null;
  decision_at: string | null;
  decision_by_user_id: string | null;
  rejection_reason: string | null;
  imported_at: string | null;
  import_result: string | null;
  import_failure_reason: string | null;
};

type SupplierCandidateResponse = { candidates: SupplierCandidate[]; total: number };

type BulkImportResult = {
  requested_id: string;
  status: "IMPORTED" | "ALREADY_EXISTS" | "ALREADY_IMPORTED" | "REJECTED_NOT_APPROVED" | "FAILED";
  canonical_supplier_product_id: string | null;
  product_id: string | null;
  message: string;
};

type BulkImportResponse = {
  supplier: "cj";
  requested_count: number;
  imported_count: number;
  already_exists_count: number;
  already_imported_count: number;
  rejected_not_approved_count: number;
  failed_count: number;
  results: BulkImportResult[];
};

type MarketEvidence = {
  id: string;
  competitor_name: string;
  product_name: string;
  source_url: string;
  observed_price_inr: number;
  currency: "INR";
  variant_description: string | null;
  notes: string | null;
  checked_at: string;
};

type MarketEvidenceResponse = {
  evidence: MarketEvidence[];
  analysis: {
    observation_count: number;
    minimum_price_inr: number | null;
    maximum_price_inr: number | null;
    average_price_inr: number | null;
    median_price_inr: number | null;
    status: "INSUFFICIENT_MARKET_DATA" | "MARKET_EVIDENCE_AVAILABLE" | "MARKET_COMPETITIVE" | "MARKET_ABOVE_OBSERVED";
    evaluated_variant_count: number;
    letrusto_variant_min_price_inr: number | null;
    letrusto_variant_max_price_inr: number | null;
  };
};

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

const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatInr(value: number) {
  return `₹${inrFormatter.format(value)}`;
}

function formatUsd(value: number) {
  return usdFormatter.format(value);
}

function printfulPricing(product: Product) {
  const pricing = product.supplier_validation_details?.printful_customer_pricing;
  if (!pricing || typeof pricing !== "object") return { india_price_inr: "", international_price_usd: "", shipping_reviewed: false };
  const data = pricing as { india_price_inr?: string; international_price_usd?: string; shipping_reviewed?: boolean };
  return {
    india_price_inr: data.india_price_inr ?? "",
    international_price_usd: data.international_price_usd ?? "",
    shipping_reviewed: data.shipping_reviewed === true,
  };
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
  const [candidates, setCandidates] = useState<SupplierCandidate[]>([]);
  const [candidateEvidence, setCandidateEvidence] = useState<Record<string, MarketEvidenceResponse>>({});
  const [supplierProductId, setSupplierProductId] = useState("");
  const [candidateIdentifier, setCandidateIdentifier] = useState("");
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>([]);
  const [bulkImportResult, setBulkImportResult] = useState<BulkImportResponse | null>(null);
  const [printfulConnection, setPrintfulConnection] = useState<PrintfulConnection | null>(null);
  const [printfulProducts, setPrintfulProducts] = useState<PrintfulProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [printfulWorking, setPrintfulWorking] = useState(false);
  const [importingPrintfulId, setImportingPrintfulId] = useState<string | null>(null);
  const [candidateWorking, setCandidateWorking] = useState(false);
  const [rejectingCandidateId, setRejectingCandidateId] = useState<string | null>(null);
  const [candidateRejectionReason, setCandidateRejectionReason] = useState("");
  const [bulkWorking, setBulkWorking] = useState(false);
  const [syncingProductId, setSyncingProductId] = useState<string | null>(null);
  const [reviewingProductId, setReviewingProductId] = useState<string | null>(null);
  const [decidingProductId, setDecidingProductId] = useState<string | null>(null);
  const [rejectingProductId, setRejectingProductId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");
  const [calculatingProductId, setCalculatingProductId] = useState<string | null>(null);
  const [deletingProductId, setDeletingProductId] = useState<string | null>(null);
  const [pricingInputs, setPricingInputs] = useState<Record<string, PricingInputs>>({});
  const [priceCalculations, setPriceCalculations] = useState<Record<string, PriceCalculation | VariantPriceCalculation>>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [fulfillmentOrders, setFulfillmentOrders] = useState<FulfillmentOrder[]>([]);
  const [syncingOrderId, setSyncingOrderId] = useState<string | null>(null);
  const [productFilter, setProductFilter] = useState<"all" | "drafts" | "published">("all");

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const status = productFilter === "drafts" ? "DRAFT" : productFilter === "published" ? "ACTIVE" : "";
      const query = status ? `?status=${status}` : "";
      const response = await fetch(`${API_BASE}/api/v1/admin/products${query}`, { headers: apiHeaders() });
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
  }, [productFilter]);

  const loadCandidates = useCallback(async () => {
    const response = await fetch(`${API_BASE}/api/v1/admin/supplier-candidates`, { headers: apiHeaders() });
    if (!response.ok) throw new Error(await apiError(response));
    const data = (await response.json()) as SupplierCandidateResponse;
    setCandidates(data.candidates);
  }, []);

  const loadFulfillmentOrders = useCallback(async () => {
    const response = await fetch(`${API_BASE}/api/v1/admin/orders/fulfillment`, { headers: apiHeaders() });
    if (!response.ok) throw new Error(await apiError(response));
    setFulfillmentOrders((await response.json()) as FulfillmentOrder[]);
  }, []);

  async function loadCandidateEvidence(candidateId: string) {
    if (candidateEvidence[candidateId]) return;
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/supplier-candidates/${candidateId}/market-evidence`, { headers: apiHeaders() });
      if (!response.ok) throw new Error(await apiError(response));
      const data = (await response.json()) as MarketEvidenceResponse;
      setCandidateEvidence((current) => ({ ...current, [candidateId]: data }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load candidate market evidence");
    }
  }

  useEffect(() => {
    void Promise.resolve()
      .then(() => Promise.all([loadProducts(), loadCandidates(), loadFulfillmentOrders()]))
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Unable to load supplier candidates");
      });
  }, [loadCandidates, loadFulfillmentOrders, loadProducts]);

  async function syncFulfillment(orderId: string) {
    setSyncingOrderId(orderId);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/orders/${orderId}/sync-fulfillment`, { method: "POST", headers: apiHeaders() });
      if (!response.ok) throw new Error(await apiError(response));
      await loadFulfillmentOrders();
      setMessage("Fulfillment status synchronized.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to synchronize fulfillment");
    } finally {
      setSyncingOrderId(null);
    }
  }

  async function testPrintfulConnection() {
    setPrintfulWorking(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/printful/connection`, { headers: apiHeaders() });
      if (!response.ok) throw new Error(await apiError(response));
      const result = (await response.json()) as PrintfulConnection;
      setPrintfulConnection(result);
      setMessage(result.connected ? `Printful connection: ${result.status}` : result.message ?? "Printful connection failed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to test Printful connection");
    } finally {
      setPrintfulWorking(false);
    }
  }

  async function loadPrintfulProducts() {
    setPrintfulWorking(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/printful/products`, { headers: apiHeaders() });
      if (!response.ok) throw new Error(await apiError(response));
      const result = (await response.json()) as PrintfulProductsResponse;
      setPrintfulProducts(result.products);
      setMessage(`Printful products found: ${result.total}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load Printful products");
    } finally {
      setPrintfulWorking(false);
    }
  }

  async function importPrintfulHoodie(product: PrintfulProduct) {
    setImportingPrintfulId(product.supplier_product_id);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/printful/products/${encodeURIComponent(product.supplier_product_id)}/import-hoodie`, {
        method: "POST",
        headers: apiHeaders(),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const imported = (await response.json()) as Product;
      setMessage(`${imported.name} imported as DRAFT.`);
      await Promise.all([loadProducts(), loadPrintfulProducts()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import Printful hoodie");
    } finally {
      setImportingPrintfulId(null);
    }
  }

  async function archiveLegacyCjProducts() {
    setPrintfulWorking(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/archive-legacy-cj`, { method: "POST", headers: apiHeaders() });
      if (!response.ok) throw new Error(await apiError(response));
      const result = (await response.json()) as LegacyArchiveResponse;
      setMessage(`Archived ${result.archived_count} legacy supplier product${result.archived_count === 1 ? "" : "s"}.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to archive legacy supplier products");
    } finally {
      setPrintfulWorking(false);
    }
  }

  async function savePrintfulPricing(product: Product, payload: { india_price_inr: string; international_price_usd: string; shipping_reviewed: boolean }) {
    setPrintfulWorking(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/printful-pricing`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify({
          india_price_inr: payload.india_price_inr,
          international_price_usd: payload.international_price_usd,
          shipping_reviewed: payload.shipping_reviewed,
        }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage(`Printful pricing saved for ${product.name}.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save Printful pricing");
    } finally {
      setPrintfulWorking(false);
    }
  }

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

  async function registerCandidate(event: React.FormEvent) {
    event.preventDefault();
    if (!candidateIdentifier.trim()) return;
    setCandidateWorking(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/supplier-candidates`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify({ supplier: "cj", supplier_product_id: candidateIdentifier.trim(), destination: "IN" }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setCandidateIdentifier("");
      setMessage("Supplier candidate verified and staged for review.");
      await loadCandidates();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to register supplier candidate");
    } finally {
      setCandidateWorking(false);
    }
  }

  async function decideCandidate(candidate: SupplierCandidate, action: "approve" | "reject", reason?: string) {
    setCandidateWorking(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/supplier-candidates/${candidate.id}/${action}`, {
        method: "POST",
        headers: action === "reject" ? { "Content-Type": "application/json", ...apiHeaders() } : apiHeaders(),
        body: action === "reject" ? JSON.stringify({ reason }) : undefined,
      });
      if (!response.ok) throw new Error(await apiError(response));
      setSelectedCandidateIds((current) => current.filter((id) => id !== candidate.supplier_product_id));
      setRejectingCandidateId(null);
      setCandidateRejectionReason("");
      await loadCandidates();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Unable to ${action} supplier candidate`);
    } finally {
      setCandidateWorking(false);
    }
  }

  function toggleBulkSelection(supplierProductId: string) {
    setSelectedCandidateIds((current) =>
      current.includes(supplierProductId)
        ? current.filter((productId) => productId !== supplierProductId)
        : [...current, supplierProductId],
    );
  }

  async function bulkImportApprovedProducts() {
    if (selectedCandidateIds.length === 0) return;
    setBulkWorking(true);
    setError("");
    setMessage("");
    setBulkImportResult(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/bulk-import`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify({ supplier: "cj", product_ids: selectedCandidateIds }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const result = (await response.json()) as BulkImportResponse;
      setBulkImportResult(result);
      setSelectedCandidateIds([]);
      await Promise.all([loadCandidates(), loadProducts()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to process approved products");
    } finally {
      setBulkWorking(false);
    }
  }

  async function runFinalAction(product: Product, action: "approve" | "reject" | "activate" | "pause") {
    setDecidingProductId(product.id);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: action === "reject" ? JSON.stringify({ reason: rejectionReason.trim() || null }) : undefined,
      });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage(`${product.name} ${action === "approve" ? "approved" : action === "reject" ? "rejected" : action === "activate" ? "activated" : "paused"}.`);
      setRejectingProductId(null);
      setRejectionReason("");
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Unable to ${action} product`);
    } finally {
      setDecidingProductId(null);
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

  async function deleteProduct(product: Product) {
    if (!window.confirm(`Permanently delete ${product.name}? This cannot be undone.`)) return;
    setDeletingProductId(product.id);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}`, {
        method: "DELETE",
        headers: apiHeaders(),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage(`${product.name} deleted.`);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete product");
    } finally {
      setDeletingProductId(null);
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
          <p className="text-sm text-[var(--text-muted)] mt-1">Printful POD products and publish status.</p>
        </div>
        <span className="text-sm text-[var(--text-muted)]">{products.length} loaded</span>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {(["all", "drafts", "published"] as const).map((filter) => <button key={filter} type="button" onClick={() => setProductFilter(filter)} className={`lt-btn lt-btn-secondary capitalize ${productFilter === filter ? "border-[var(--lt-primary)] text-[var(--lt-primary)]" : ""}`}>{filter}</button>)}
      </div>

      {LEGACY_CJ_WORKFLOW_ENABLED && <form onSubmit={(event) => void importProduct(event)} className="lt-card p-4 mb-6 flex flex-col sm:flex-row gap-3">
        <input
          value={supplierProductId}
          onChange={(event) => setSupplierProductId(event.target.value)}
          placeholder="Legacy supplier product ID"
          className="lt-input flex-1"
          aria-label="Legacy supplier product ID"
        />
        <button type="submit" disabled={working} className="lt-btn lt-btn-primary">
          {working ? "Importing..." : "Import as Draft"}
        </button>
      </form>}

      <section className="lt-card mb-6 p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold">POD / Printful</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">Test the backend-only Printful connection, discover finalized POD products, and import Unisex Hoodie as DRAFT.</p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button type="button" onClick={() => void testPrintfulConnection()} disabled={printfulWorking} className="lt-btn lt-btn-secondary">
              <RefreshCw size={16} />
              Test Connection
            </button>
            <button type="button" onClick={() => void loadPrintfulProducts()} disabled={printfulWorking} className="lt-btn lt-btn-primary">
              {printfulWorking ? "Loading..." : "Find Products"}
            </button>
            <button type="button" onClick={() => void archiveLegacyCjProducts()} disabled={printfulWorking} className="lt-btn lt-btn-secondary">
              Archive Legacy Catalog
            </button>
          </div>
        </div>
        {printfulConnection && <p className="mt-4 text-sm font-semibold text-[var(--text-primary)]">Printful connection: {printfulConnection.connected ? "Connected" : "Unavailable"}{printfulConnection.store ? ` · Store: ${printfulConnection.store}` : ""}{printfulConnection.message ? ` · ${printfulConnection.message}` : ""}</p>}
        {printfulProducts.length > 0 && <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {printfulProducts.map((product) => {
            const isHoodie = product.name.trim().toLowerCase() === "unisex hoodie";
            return <article key={product.supplier_product_id} className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-3">
              {product.thumbnail_url && <Image src={product.thumbnail_url} alt="" width={96} height={96} className="mb-3 h-24 w-24 rounded-lg object-cover" unoptimized />}
              <h3 className="font-semibold text-[var(--text-primary)]">{product.name}</h3>
              <p className="mt-1 text-xs text-[var(--text-muted)]">Printful ID: {product.supplier_product_id}</p>
              <button type="button" disabled={!isHoodie || importingPrintfulId === product.supplier_product_id} onClick={() => void importPrintfulHoodie(product)} className="lt-btn lt-btn-primary mt-3 w-full disabled:opacity-50">
                {product.imported_product_id ? "Update Draft" : importingPrintfulId === product.supplier_product_id ? "Importing..." : isHoodie ? "Import as Draft" : "Later"}
              </button>
            </article>;
          })}
        </div>}
      </section>

      {LEGACY_CJ_WORKFLOW_ENABLED && <section className="mb-6 border-y border-[var(--border)] py-5">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Legacy Supplier Candidates</h2>
            <p className="text-sm text-[var(--text-muted)] mt-1">Legacy supplier products awaiting an explicit import decision.</p>
          </div>
          <form onSubmit={(event) => void registerCandidate(event)} className="flex flex-col sm:flex-row gap-2 lg:w-[32rem]">
            <input value={candidateIdentifier} onChange={(event) => setCandidateIdentifier(event.target.value)} placeholder="Legacy supplier product ID or SKU" aria-label="Legacy supplier product ID or SKU" className="lt-input flex-1" />
            <button type="submit" disabled={candidateWorking} className="lt-btn lt-btn-primary">{candidateWorking ? "Verifying..." : "Register"}</button>
          </form>
        </div>
        {candidates.length === 0 ? (
          <p className="mt-4 text-sm text-[var(--text-muted)]">No supplier candidates staged.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm whitespace-nowrap">
              <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2 pr-3"><span className="sr-only">Select</span></th><th className="pr-3">Candidate</th><th className="pr-3">CJ ID / SKU</th><th className="pr-3">Validation</th><th className="pr-3">Commercial</th><th className="pr-3">Market</th><th className="pr-3">Approval</th><th><span className="sr-only">Actions</span></th></tr></thead>
              <tbody>{candidates.map((candidate) => (
                <Fragment key={candidate.id}>
                <tr className="border-t border-[var(--border)]">
                  <td className="py-3 pr-3"><input type="checkbox" disabled={candidate.approval_status !== "APPROVED"} checked={selectedCandidateIds.includes(candidate.supplier_product_id)} onChange={() => toggleBulkSelection(candidate.supplier_product_id)} aria-label={`Select ${candidate.name} for import`} className="h-4 w-4" /></td>
                  <td className="pr-3 font-semibold max-w-72" title={candidate.name}>
                    <span className="block truncate">{candidate.name}</span>
                    <details className="mt-1 text-xs font-normal text-[var(--text-muted)]">
                      <summary className="cursor-pointer">Validation, pricing and variants</summary>
                      <div className="mt-2 max-w-[42rem] space-y-2 whitespace-normal">
                        <p className="font-semibold">Readiness: {candidate.readiness_status}</p>
                        <p className="font-semibold">{candidate.snapshot_status === "AVAILABLE" ? "Variant snapshot available" : "Variant snapshot unavailable because this candidate predates snapshot capture"}</p>
                        {candidate.snapshot_status === "AVAILABLE" && candidate.main_image && <Image src={candidate.main_image} alt="" width={48} height={48} className="h-12 w-12 object-cover rounded" />}
                        <p>Price range: {candidate.discovery_min_selling_price_inr == null ? "-" : formatInr(candidate.discovery_min_selling_price_inr)} to {candidate.discovery_max_selling_price_inr == null ? "-" : formatInr(candidate.discovery_max_selling_price_inr)} · Target margin {candidate.target_margin_percent ?? "-"}% · CAC {candidate.cac_viable == null ? "NOT REVIEWED" : candidate.cac_viable ? "VIABLE" : "NOT VIABLE"}</p>
                        {candidate.snapshot_status === "AVAILABLE" && <p>Inventory: {candidate.variants.reduce((sum, variant) => sum + (variant.cj_inventory ?? 0), 0)} CJ sellable · {candidate.variants.reduce((sum, variant) => sum + (variant.factory_inventory ?? 0), 0)} factory</p>}
                        <p>India freight: {candidate.freight.available ? "AVAILABLE" : "UNAVAILABLE"} · {candidate.freight.cost_inr == null ? "-" : formatInr(Number(candidate.freight.cost_inr))} · {candidate.freight.delivery_estimate ?? "No delivery estimate"}</p>
                        <p>Logistics: {candidate.logistics.selected ? `${candidate.logistics.selected.carrier ?? "Carrier"} / ${candidate.logistics.selected.method ?? "Method"}` : "No selected route"} · Warehouse: {candidate.warehouses.length || "-"}</p>
                        {candidate.warehouses.length > 0 && <p>Warehouses: {candidate.warehouses.map((warehouse) => `${warehouse.warehouse_name ?? warehouse.storage_id ?? "Unknown"} (${warehouse.cj_inventory ?? 0} sellable)`).join(", ")}</p>}
                        <p>Proposed price: {candidate.commercial_result.minimum_price_inr == null ? "-" : `${formatInr(Number(candidate.commercial_result.minimum_price_inr))} to ${formatInr(Number(candidate.commercial_result.maximum_price_inr ?? candidate.commercial_result.minimum_price_inr))}`} · Margin {candidate.commercial_result.target_margin_percent ?? candidate.target_margin_percent ?? "-"}%</p>
                        {candidate.validation_issues.length > 0 && <p>Validation issues: {candidate.validation_issues.join(", ")}</p>}
                        {candidate.snapshot_status === "AVAILABLE" && <div className="overflow-x-auto">
                          <table className="w-full text-xs"><thead><tr className="text-left"><th className="pr-2">Variant</th><th className="pr-2">Cost</th><th className="pr-2">Weight</th><th>CJ / factory</th></tr></thead><tbody>{candidate.variants.map((variant) => <tr key={variant.supplier_variant_id}><td className="pr-2">{variant.supplier_variant_id} · {variant.supplier_variant_sku}</td><td className="pr-2">{variant.supplier_cost_usd == null ? "-" : `$${variant.supplier_cost_usd}`} / {variant.supplier_cost_inr == null ? "-" : formatInr(variant.supplier_cost_inr)}</td><td className="pr-2">{variant.weight_grams == null ? "-" : `${variant.weight_grams}g`}</td><td>{variant.cj_inventory ?? 0} / {variant.factory_inventory ?? 0}</td></tr>)}</tbody></table>
                        </div>}
                      </div>
                    </details>
                    <details className="mt-1 text-xs font-normal text-[var(--text-muted)]" onToggle={(event) => { if (event.currentTarget.open) void loadCandidateEvidence(candidate.id); }}>
                      <summary className="cursor-pointer">Evidence ({candidate.market_evidence_count})</summary>
                      {candidateEvidence[candidate.id] && <div className="mt-2 max-w-80 space-y-2 whitespace-normal">
                        {candidateEvidence[candidate.id].evidence.length === 0 ? <p>No observations.</p> : candidateEvidence[candidate.id].evidence.map((evidence) => <div key={evidence.id} className="border-t border-[var(--border)] pt-1"><a href={evidence.source_url} target="_blank" rel="noopener noreferrer" className="font-semibold underline">{evidence.competitor_name}</a> · {formatInr(evidence.observed_price_inr)}<p>{evidence.variant_description ?? "Comparable listing"}</p><p>{new Date(evidence.checked_at).toLocaleDateString("en-IN")}</p></div>)}
                      </div>}
                    </details>
                  </td>
                  <td className="pr-3"><span className="block">{candidate.supplier_product_id}</span><span className="text-xs text-[var(--text-muted)]">{candidate.supplier_sku ?? "No SKU"}</span></td>
                  <td className="pr-3">{candidate.readiness_status}<span className="block text-xs text-[var(--text-muted)]">{candidate.supplier_validation_status ?? "-"} {candidate.supplier_validation_score ?? "-"}</span></td>
                  <td className="pr-3">{candidate.commercial_status}</td>
                  <td className="pr-3">{candidate.market_status} ({candidate.market_evidence_count})</td>
                  <td className="pr-3">{candidate.approval_status}</td>
                  <td><div className="flex gap-2">
                    {(candidate.approval_status === "REVIEW" || candidate.approval_status === "REJECTED") && candidate.readiness_status !== "REJECTED" && <button type="button" disabled={candidateWorking} onClick={() => void decideCandidate(candidate, "approve")} className="lt-btn lt-btn-primary p-2" title="Approve candidate" aria-label={`Approve ${candidate.name}`}><Check size={16} aria-hidden="true" /></button>}
                    {candidate.approval_status !== "IMPORTED" && candidate.approval_status !== "REJECTED" && <button type="button" disabled={candidateWorking} onClick={() => { setRejectingCandidateId(candidate.id); setCandidateRejectionReason(""); }} className="lt-btn lt-btn-secondary p-2" title="Reject candidate" aria-label={`Reject ${candidate.name}`}><X size={16} aria-hidden="true" /></button>}
                  </div></td>
                </tr>
              {rejectingCandidateId === candidate.id && <tr><td colSpan={8} className="border-t border-[var(--border)] py-3"><form onSubmit={(event) => { event.preventDefault(); void decideCandidate(candidate, "reject", candidateRejectionReason.trim()); }} className="flex flex-col sm:flex-row gap-2"><input required minLength={1} maxLength={500} value={candidateRejectionReason} onChange={(event) => setCandidateRejectionReason(event.target.value)} placeholder="Rejection reason" aria-label={`Rejection reason for ${candidate.name}`} className="lt-input flex-1" /><button type="submit" disabled={candidateWorking || !candidateRejectionReason.trim()} className="lt-btn lt-btn-secondary">Confirm rejection</button><button type="button" onClick={() => setRejectingCandidateId(null)} className="lt-btn lt-btn-secondary">Cancel</button></form></td></tr>}
                </Fragment>
                ))}</tbody>
            </table>
          </div>
        )}
      </section>}

      {LEGACY_CJ_WORKFLOW_ENABLED && selectedCandidateIds.length > 0 && (
        <div className="mb-4 flex items-center justify-between gap-3 border border-[var(--border)] p-3">
          <span className="text-sm">{selectedCandidateIds.length} approved candidate{selectedCandidateIds.length === 1 ? "" : "s"} selected</span>
          <button type="button" disabled={bulkWorking} onClick={() => void bulkImportApprovedProducts()} className="lt-btn lt-btn-primary text-sm">
            {bulkWorking ? "Processing..." : "Bulk Import Selected"}
          </button>
        </div>
      )}

      {LEGACY_CJ_WORKFLOW_ENABLED && bulkImportResult && (
        <section className="mb-4 border border-[var(--border)] p-4" aria-live="polite">
          <h2 className="font-semibold text-sm">Bulk approved import result</h2>
          <p className="mt-1 text-sm text-[var(--text-muted)]">
            Requested {bulkImportResult.requested_count} · Imported {bulkImportResult.imported_count} · Already exists {bulkImportResult.already_exists_count} · Already imported {bulkImportResult.already_imported_count} · Not approved {bulkImportResult.rejected_not_approved_count} · Failed {bulkImportResult.failed_count}
          </p>
          <ul className="mt-3 space-y-2 text-xs">
            {bulkImportResult.results.map((result, index) => (
              <li key={`${result.requested_id}-${index}`} className="border-t border-[var(--border)] pt-2">
                <span className="font-semibold">{result.canonical_supplier_product_id ?? result.requested_id}: {result.status.replaceAll("_", " ")}</span>
                <span className="block text-[var(--text-muted)]">{result.message}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {message && <p className="mb-4 text-sm text-green-700">{message}</p>}
      {error && <p className="mb-4 text-sm text-red-700">{error}</p>}

      {LEGACY_CJ_WORKFLOW_ENABLED && <FulfillmentPreflightPanel products={products.map((product) => ({ id: product.id, name: product.name, variants: product.variants }))} />}

      {LEGACY_CJ_WORKFLOW_ENABLED && <section className="mb-6 border-y border-[var(--border)] py-5">
        <h2 className="text-lg font-semibold">Paid order fulfillment</h2>
        <p className="text-sm text-[var(--text-muted)] mt-1">Supplier status and tracking are synchronized server-side.</p>
        {fulfillmentOrders.length === 0 ? <p className="mt-4 text-sm text-[var(--text-muted)]">No paid orders require fulfillment.</p> : <div className="mt-4 overflow-x-auto"><table className="w-full text-sm whitespace-nowrap"><thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2 pr-3">Order</th><th className="pr-3">Payment</th><th className="pr-3">Fulfillment</th><th className="pr-3">CJ order</th><th className="pr-3">Tracking</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{fulfillmentOrders.map((order) => <tr key={order.order_id} className="border-t border-[var(--border)]"><td className="py-3 pr-3">{order.order_number}<span className="block text-xs text-[var(--text-muted)]">{order.customer_email}</span></td><td className="pr-3">{order.payment_status}</td><td className="pr-3">{order.fulfillment_status}<span className="block text-xs text-[var(--text-muted)]">{order.supplier_status ?? "-"}</span></td><td className="pr-3">{order.supplier_order_id ?? "Not submitted"}</td><td className="pr-3">{order.tracking_number ? `${order.tracking_carrier ?? "Carrier"} · ${order.tracking_number}` : "-"}</td><td><button type="button" onClick={() => void syncFulfillment(order.order_id)} disabled={syncingOrderId !== null || order.fulfillment_status === "DELIVERED"} className="lt-btn lt-btn-secondary text-sm">{syncingOrderId === order.order_id ? "Syncing..." : "Sync status"}</button></td></tr>)}</tbody></table></div>}
      </section>}

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
                    <p className="text-xs text-[var(--text-muted)] mt-1">Supplier: {product.supplier ?? "-"} · ID: {product.supplier_product_id ?? "-"}</p>
                    <p className="text-xs text-[var(--text-muted)]">Variants: {product.variants.length} · Images: {product.images.length}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center justify-end gap-2">
                  {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && product.commercial_status !== "APPROVED" && product.commercial_status !== "REJECTED" && (
                    <button type="button" disabled={reviewingProductId !== null || decidingProductId !== null} onClick={() => void runCommercialReview(product)} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2">
                      <ClipboardCheck size={16} aria-hidden="true" />
                      {reviewingProductId === product.id ? "Reviewing..." : "Run Commercial Review"}
                    </button>
                  )}
                  {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && product.commercial_status === "REVIEW" && product.status !== "ACTIVE" && (
                    <button type="button" disabled={decidingProductId !== null} onClick={() => void runFinalAction(product, "approve")} className="lt-btn lt-btn-primary text-sm inline-flex items-center gap-2">
                      <Check size={16} aria-hidden="true" />
                      {decidingProductId === product.id ? "Working..." : "Approve"}
                    </button>
                  )}
                  {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && (product.commercial_status === "REVIEW" || product.commercial_status === "APPROVED") && product.status !== "ACTIVE" && (
                    <button type="button" disabled={decidingProductId !== null} onClick={() => { setRejectingProductId(product.id); setRejectionReason(""); }} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2">
                      <X size={16} aria-hidden="true" /> Reject
                    </button>
                  )}
                  {product.supplier === "printful" && (product.status === "DRAFT" || product.status === "PAUSED") && (
                    <button type="button" disabled={decidingProductId !== null} onClick={() => void runFinalAction(product, "activate")} className="lt-btn lt-btn-primary text-sm inline-flex items-center gap-2">
                      <Play size={16} aria-hidden="true" />
                      {decidingProductId === product.id ? "Working..." : "Publish"}
                    </button>
                  )}
                  {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && product.commercial_status === "APPROVED" && (product.status === "DRAFT" || product.status === "PAUSED") && (
                    <button type="button" disabled={decidingProductId !== null} onClick={() => void runFinalAction(product, "activate")} className="lt-btn lt-btn-primary text-sm inline-flex items-center gap-2">
                      <Play size={16} aria-hidden="true" />
                      {decidingProductId === product.id ? "Working..." : "Activate"}
                    </button>
                  )}
                  {product.status === "ACTIVE" && (
                    <button type="button" disabled={decidingProductId !== null} onClick={() => void runFinalAction(product, "pause")} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2">
                      <CirclePause size={16} aria-hidden="true" />
                      {decidingProductId === product.id ? "Working..." : "Pause"}
                    </button>
                  )}
                  {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && <button type="button" disabled={syncingProductId !== null} onClick={() => void syncInventory(product)} className="lt-btn lt-btn-secondary text-sm">
                    {syncingProductId === product.id ? "Syncing..." : "Sync Inventory"}
                  </button>}
                  <Link href={`/admin/products/${product.id}/trust`} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2">
                    <ClipboardCheck size={16} aria-hidden="true" />
                    Trust
                  </Link>
                  <button type="button" disabled={deletingProductId !== null} onClick={() => void deleteProduct(product)} className="lt-btn lt-btn-secondary text-sm inline-flex items-center gap-2" title="Permanently delete product" aria-label={`Delete ${product.name}`}>
                    <Trash2 size={16} aria-hidden="true" />
                    {deletingProductId === product.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </div>
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && rejectingProductId === product.id && (
                <form onSubmit={(event) => { event.preventDefault(); void runFinalAction(product, "reject"); }} className="mt-4 border-t border-[var(--border)] pt-4 flex flex-col sm:flex-row items-end gap-3">
                  <label className="text-xs text-[var(--text-muted)] flex-1 w-full">
                    <span>Rejection reason (optional)</span>
                    <input value={rejectionReason} onChange={(event) => setRejectionReason(event.target.value)} maxLength={500} className="lt-input w-full mt-1 text-sm" />
                  </label>
                  <button type="submit" disabled={decidingProductId !== null} className="lt-btn lt-btn-primary text-sm">Confirm Reject</button>
                  <button type="button" disabled={decidingProductId !== null} onClick={() => { setRejectingProductId(null); setRejectionReason(""); }} className="lt-btn lt-btn-secondary text-sm">Cancel</button>
                </form>
              )}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4 text-sm">
                <Metric label="Status" value={product.status} />
                <Metric label="POD availability" value={product.verified_warehouse ?? "Review"} />
                <Metric label="Inventory" value={product.total_inventory ?? "On demand"} />
                <Metric label="Supplier cost" value={product.supplier_cost == null ? "-" : formatInr(product.supplier_cost)} />
                <Metric label="Shipping" value={product.shipping_cost == null ? "Not configured" : formatInr(product.shipping_cost)} />
                <Metric label="Selling price" value={product.selling_price == null ? "-" : formatInr(product.selling_price)} />
              </div>
              {product.supplier === "printful" && <PrintfulProductWorkflow product={product} working={printfulWorking} onSave={(payload) => void savePrintfulPricing(product, payload)} />}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 border-t border-[var(--border)] pt-4 text-sm">
                <Metric label="Commercial status" value={product.commercial_status} />
                <Metric label="Target margin" value={product.commercial_target_margin_percent == null ? "-" : `${product.commercial_target_margin_percent}%`} />
                <Metric label="CAC target" value={product.commercial_target_cac_inr == null ? "-" : formatInr(product.commercial_target_cac_inr)} />
                <Metric label="CAC supported" value={product.commercial_cac_supported == null ? "NOT REVIEWED" : product.commercial_cac_supported ? "YES" : "NO"} />
                <Metric label="Market price" value={product.market_price_status} />
              </div>}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4 border-t border-[var(--border)] pt-4 text-sm">
                <Metric label="Supplier validation" value={product.supplier_validation_status ?? "NOT AVAILABLE"} />
                <Metric label="Validation score" value={product.supplier_validation_score ?? "-"} />
                <Metric label="Validated" value={product.supplier_validated_at ? new Date(product.supplier_validated_at).toLocaleString("en-IN") : "-"} />
              </div>}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && (product.supplier_validation_notes ?? []).length > 0 && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">Validation issues: {(product.supplier_validation_notes ?? []).join(", ")}</p>
              )}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && product.commercial_reasons.length > 0 && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">Reasons: {product.commercial_reasons.join(", ")}</p>
              )}
              {product.approval_rejection_reason && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">Rejection reason: {product.approval_rejection_reason}</p>
              )}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && <details className="mt-4 border-t border-[var(--border)] pt-4">
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
              </details>}
              {product.supplier !== "printful" && LEGACY_CJ_WORKFLOW_ENABLED && <MarketEvidenceSection product={product} onError={setError} onMessage={setMessage} />}
              {product.variants.length > 0 && (
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2">Variant ID</th><th>SKU</th><th>Supplier USD</th><th>Supplier cost (INR)</th><th>Selling price</th><th>Inventory</th><th>Reserved supply</th></tr></thead>
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

function PrintfulProductWorkflow({ product, working, onSave }: { product: Product; working: boolean; onSave: (payload: { india_price_inr: string; international_price_usd: string; shipping_reviewed: boolean }) => void }) {
  const savedPricing = printfulPricing(product);
  const [indiaPrice, setIndiaPrice] = useState(savedPricing.india_price_inr);
  const [internationalPrice, setInternationalPrice] = useState(savedPricing.international_price_usd);
  const [shippingReviewed, setShippingReviewed] = useState(savedPricing.shipping_reviewed);
  const activeVariants = product.variants.filter((variant) => variant.active);
  const baseCost = activeVariants[0]?.supplier_cost_usd ?? product.supplier_cost;
  const highestCost = activeVariants.reduce<number | null>((max, variant) => {
    if (variant.supplier_cost_usd == null) return max;
    return max == null ? variant.supplier_cost_usd : Math.max(max, variant.supplier_cost_usd);
  }, null);
  const checklist = [
    ["Printful product ID exists", Boolean(product.supplier_product_id)],
    ["At least one valid variant", activeVariants.length > 0],
    ["Active variants have SKU", activeVariants.every((variant) => Boolean(variant.supplier_variant_id && variant.supplier_variant_sku))],
    ["Product images/mockups available", product.images.length > 0],
    ["Product title exists", Boolean(product.name.trim())],
    ["Product description exists", Boolean(product.description.trim())],
    ["India price configured", Boolean(savedPricing.india_price_inr)],
    ["International USD price configured", Boolean(savedPricing.international_price_usd)],
    ["Shipping configuration reviewed", savedPricing.shipping_reviewed],
    ["Supplier = Printful", product.supplier === "printful"],
    ["Product status ready for publication", product.status === "DRAFT" || product.status === "PAUSED" || product.status === "ACTIVE"],
  ] as const;

  return <section className="mt-4 border-t border-[var(--border)] pt-4">
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
        <h3 className="font-semibold text-[var(--text-primary)]">Printful Cost</h3>
        <div className="mt-3 space-y-2 text-sm">
          <Metric label="Base fulfillment cost" value={baseCost == null ? "Not available" : formatUsd(Number(baseCost))} />
          <Metric label="Highest variant cost" value={highestCost == null ? "Not available" : formatUsd(highestCost)} />
          <Metric label="Supplier product ID" value={product.supplier_product_id ?? "-"} />
        </div>
      </div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
        <h3 className="font-semibold text-[var(--text-primary)]">Shipping</h3>
        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          {['India', 'United States', 'United Kingdom', 'European Union', 'Rest of World'].map((region) => <Metric key={region} label={region} value="Not configured" />)}
        </div>
        <label className="mt-4 flex items-center gap-2 text-sm text-[var(--text-secondary)]"><input type="checkbox" checked={shippingReviewed} onChange={(event) => setShippingReviewed(event.target.checked)} /> Shipping reviewed</label>
      </div>
      <form onSubmit={(event) => { event.preventDefault(); onSave({ india_price_inr: indiaPrice, international_price_usd: internationalPrice, shipping_reviewed: shippingReviewed }); }} className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
        <h3 className="font-semibold text-[var(--text-primary)]">LeTrusto Customer Price</h3>
        <div className="mt-3 space-y-3">
          <label className="block text-xs font-semibold text-[var(--text-secondary)]">India<input type="number" min="0" step="0.01" required value={indiaPrice} onChange={(event) => setIndiaPrice(event.target.value)} className="lt-input mt-1 h-11" placeholder="INR" /></label>
          <label className="block text-xs font-semibold text-[var(--text-secondary)]">International<input type="number" min="0" step="0.01" required value={internationalPrice} onChange={(event) => setInternationalPrice(event.target.value)} className="lt-input mt-1 h-11" placeholder="USD" /></label>
          <button type="submit" disabled={working} className="lt-btn lt-btn-primary h-11 w-full">{working ? "Saving..." : "Save prices"}</button>
        </div>
      </form>
    </div>
    <div className="mt-4 grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
        <h3 className="font-semibold text-[var(--text-primary)]">Variants</h3>
        <div className="mt-3 overflow-x-auto"><table className="w-full text-xs"><thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2 pr-3">Variant</th><th className="pr-3">SKU</th><th className="pr-3">Cost</th><th>Options</th></tr></thead><tbody>{product.variants.map((variant) => <tr key={variant.id} className="border-t border-[var(--border)]"><td className="py-2 pr-3">{variant.supplier_variant_id}</td><td className="pr-3">{variant.supplier_variant_sku}</td><td className="pr-3">{variant.supplier_cost_usd == null ? "-" : formatUsd(variant.supplier_cost_usd)}</td><td>{variant.attributes || variant.name}</td></tr>)}</tbody></table></div>
      </div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
        <h3 className="font-semibold text-[var(--text-primary)]">Publish Checklist</h3>
        <ul className="mt-3 space-y-2 text-sm">{checklist.map(([label, passed]) => <li key={label} className="flex items-center gap-2"><span className={passed ? "text-green-700" : "text-[var(--text-muted)]"}>{passed ? "OK" : "TODO"}</span><span>{label}</span></li>)}</ul>
      </div>
    </div>
    {product.images.length > 0 && <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4"><h3 className="font-semibold text-[var(--text-primary)]">Mockups</h3><div className="mt-3 flex gap-3 overflow-x-auto">{product.images.map((image) => <Image key={image} src={image} alt="" width={96} height={96} className="h-24 w-24 rounded-lg object-cover" unoptimized />)}</div></div>}
  </section>;
}

function PriceInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="text-xs text-[var(--text-muted)]"><span>{label}</span><input type="number" min="0" step="any" required value={value} onChange={(event) => onChange(event.target.value)} className="lt-input w-full mt-1 text-sm" /></label>;
}

function MarketEvidenceSection({
  product,
  onError,
  onMessage,
}: {
  product: Product;
  onError: (message: string) => void;
  onMessage: (message: string) => void;
}) {
  const [data, setData] = useState<MarketEvidenceResponse | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [working, setWorking] = useState(false);

  async function loadEvidence() {
    const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/market-evidence`, {
      headers: apiHeaders(),
    });
    if (!response.ok) throw new Error(await apiError(response));
    setData((await response.json()) as MarketEvidenceResponse);
    setLoaded(true);
  }

  async function handleToggle(event: React.SyntheticEvent<HTMLDetailsElement>) {
    if (event.currentTarget.open && !loaded) {
      try {
        await loadEvidence();
      } catch (err) {
        onError(err instanceof Error ? err.message : "Unable to load market evidence");
      }
    }
  }

  async function addEvidence(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    setWorking(true);
    onError("");
    const form = new FormData(formElement);
    const checkedAt = String(form.get("checked_at") ?? "");
    const payload = {
      competitor_name: form.get("competitor_name"),
      product_name: form.get("product_name"),
      source_url: form.get("source_url"),
      observed_price_inr: form.get("observed_price_inr"),
      currency: "INR",
      variant_description: form.get("variant_description") || null,
      notes: form.get("notes") || null,
      checked_at: checkedAt ? new Date(checkedAt).toISOString() : null,
    };
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/products/${product.id}/market-evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...apiHeaders() },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(await apiError(response));
      formElement.reset();
      await loadEvidence();
      onMessage(`Market evidence added for ${product.name}.`);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unable to add market evidence");
    } finally {
      setWorking(false);
    }
  }

  async function deleteEvidence(evidenceId: string) {
    setWorking(true);
    onError("");
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/admin/products/${product.id}/market-evidence/${evidenceId}`,
        { method: "DELETE", headers: apiHeaders() },
      );
      if (!response.ok) throw new Error(await apiError(response));
      await loadEvidence();
      onMessage(`Market evidence deleted for ${product.name}.`);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unable to delete market evidence");
    } finally {
      setWorking(false);
    }
  }

  const analysis = data?.analysis;
  const variantRange = analysis?.letrusto_variant_min_price_inr == null
    ? "NOT CALCULATED"
    : analysis.letrusto_variant_min_price_inr === analysis.letrusto_variant_max_price_inr
      ? formatInr(analysis.letrusto_variant_min_price_inr)
      : `${formatInr(analysis.letrusto_variant_min_price_inr)} - ${formatInr(analysis.letrusto_variant_max_price_inr!)}`;

  return (
    <details className="mt-4 border-t border-[var(--border)] pt-4" onToggle={(event) => void handleToggle(event)}>
      <summary className="cursor-pointer text-sm font-semibold">Market Evidence</summary>
      {analysis && (
        <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3 mt-4 text-sm">
          <Metric label="Observations" value={analysis.observation_count} />
          <Metric label="Minimum" value={analysis.minimum_price_inr == null ? "-" : formatInr(analysis.minimum_price_inr)} />
          <Metric label="Maximum" value={analysis.maximum_price_inr == null ? "-" : formatInr(analysis.maximum_price_inr)} />
          <Metric label="Average" value={analysis.average_price_inr == null ? "-" : formatInr(analysis.average_price_inr)} />
          <Metric label="Median" value={analysis.median_price_inr == null ? "-" : formatInr(analysis.median_price_inr)} />
          <Metric label="Market status" value={analysis.status} />
          <Metric label={`LeTrusto variants (${analysis.evaluated_variant_count})`} value={variantRange} />
        </div>
      )}
      <form onSubmit={(event) => void addEvidence(event)} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 mt-4">
        <EvidenceInput name="competitor_name" label="Competitor name" required />
        <EvidenceInput name="product_name" label="Product name" required />
        <EvidenceInput name="source_url" label="Source URL" type="url" required />
        <EvidenceInput name="observed_price_inr" label="Observed price (INR)" type="number" min="0.01" step="0.01" required />
        <EvidenceInput name="variant_description" label="Variant description" />
        <EvidenceInput name="checked_at" label="Checked at" type="datetime-local" />
        <label className="text-xs text-[var(--text-muted)] md:col-span-2"><span>Notes</span><textarea name="notes" className="lt-input w-full mt-1 text-sm min-h-10" /></label>
        <div className="flex items-end gap-3">
          <span className="text-sm font-semibold pb-2">Currency: INR</span>
          <button type="submit" disabled={working} className="lt-btn lt-btn-primary text-sm">{working ? "Saving..." : "Add Evidence"}</button>
        </div>
      </form>
      {data && data.evidence.length === 0 && <p className="mt-4 text-sm text-[var(--text-muted)]">No market observations recorded.</p>}
      {data && data.evidence.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs">
            <thead><tr className="text-left text-[var(--text-muted)]"><th className="py-2">Competitor</th><th>Product</th><th>Variant</th><th>Price</th><th>Checked</th><th>Notes</th><th><span className="sr-only">Actions</span></th></tr></thead>
            <tbody>{data.evidence.map((evidence) => (
              <tr key={evidence.id} className="border-t border-[var(--border)]">
                <td className="py-2 pr-3">{evidence.competitor_name}</td>
                <td className="pr-3"><a href={evidence.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 underline">{evidence.product_name}<ExternalLink size={12} aria-hidden="true" /></a></td>
                <td className="pr-3">{evidence.variant_description ?? "-"}</td>
                <td className="pr-3 font-semibold">{formatInr(evidence.observed_price_inr)}</td>
                <td className="pr-3">{new Date(evidence.checked_at).toLocaleString("en-IN")}</td>
                <td className="pr-3">{evidence.notes ?? "-"}</td>
                <td><button type="button" disabled={working} onClick={() => void deleteEvidence(evidence.id)} className="lt-btn lt-btn-secondary p-2" title="Delete market evidence" aria-label={`Delete evidence from ${evidence.competitor_name}`}><Trash2 size={14} aria-hidden="true" /></button></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </details>
  );
}

function EvidenceInput({ name, label, type = "text", required = false, min, step }: { name: string; label: string; type?: string; required?: boolean; min?: string; step?: string }) {
  return <label className="text-xs text-[var(--text-muted)]"><span>{label}</span><input name={name} type={type} required={required} min={min} step={step} className="lt-input w-full mt-1 text-sm" /></label>;
}
