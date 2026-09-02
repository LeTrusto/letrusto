import { LockKeyhole } from "lucide-react";
import type { DigitalProduct } from "@/types/digital-products";
import { formatDigitalProductPrice } from "@/lib/digitalProducts";

export default function DigitalProductPurchase({ product }: { product: DigitalProduct }) {
  return (
    <aside id="purchase" className="lt-card border-[var(--lt-primary)]">
      <p className="lt-eyebrow">Digital delivery</p>
      <div className="mt-3 flex items-end justify-between gap-4"><p className="text-3xl font-black text-[var(--text-primary)]">{formatDigitalProductPrice(product)}</p><span className="text-right text-xs font-semibold text-[var(--text-muted)]">Planned launch<br />price</span></div>
      <div className="mt-6 border border-[var(--border)] bg-[var(--surface-soft)] p-4" role="status"><div className="flex items-center gap-2 text-sm font-bold text-[var(--text-primary)]"><LockKeyhole size={17} aria-hidden="true" /> Secure checkout is coming soon</div><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">This product is listed for preview only. Payment and download access are not available yet.</p></div>
      <p className="mt-4 text-xs leading-5 text-[var(--text-muted)]">When available, delivery will use a digital entitlement and protected download. This product will not be added to the physical cart or use shipping or Printful fulfillment.</p>
    </aside>
  );
}