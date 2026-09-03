"use client";

import { useEffect, useState } from "react";
import { Download, FileKey2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { downloadDigitalProduct, getDigitalPurchases, type DigitalEntitlement } from "@/services/digitalProduct.service";

export default function DigitalPurchases() {
  const { accessToken } = useAuth();
  const [purchases, setPurchases] = useState<DigitalEntitlement[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    if (accessToken) void getDigitalPurchases(accessToken).then(setPurchases).catch(() => setError("Unable to load digital purchases."));
  }, [accessToken]);
  async function download(purchase: DigitalEntitlement) {
    if (!accessToken) return;
    const blob = await downloadDigitalProduct(accessToken, purchase.product_slug);
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = `${purchase.product_slug}.csv`; anchor.click(); URL.revokeObjectURL(url);
  }
  return <section id="purchases" className="lt-card mt-8"><div className="flex items-center gap-3"><FileKey2 className="text-[var(--lt-accent-dark)]" /><div><p className="lt-label">Digital delivery</p><h2 className="text-lg font-bold">My Purchases</h2></div></div>{error && <p role="alert" className="mt-4 text-sm text-red-700">{error}</p>}{!error && purchases.length === 0 && <p className="mt-4 text-sm text-[var(--text-secondary)]">Your verified digital purchases will appear here.</p>}<div className="mt-4 grid gap-3">{purchases.map((purchase) => <div key={purchase.product_slug} className="flex flex-wrap items-center justify-between gap-4 border border-[var(--border)] bg-[var(--surface-soft)] p-4"><div><p className="font-bold">{purchase.product_name}</p><p className="mt-1 text-sm text-[var(--text-secondary)]">{purchase.currency} {purchase.amount} · Ready</p></div><button type="button" onClick={() => void download(purchase)} className="lt-btn-primary lt-btn-sm inline-flex items-center gap-2"><Download size={15} aria-hidden="true" /> Download</button></div>)}</div></section>;
}