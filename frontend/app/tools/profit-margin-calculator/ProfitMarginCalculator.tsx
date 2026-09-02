"use client";

import { useMemo, useState } from "react";
import { RotateCcw } from "lucide-react";
import { calculateProfitMargin, validateAmount, type ProfitMarginCalculation } from "@/lib/profitMarginCalculator";

const currencyFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
const percentFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });

function formatCurrency(value: number) {
  return `₹${currencyFormatter.format(value)}`;
}

function formatPercent(value: number | null) {
  return value === null ? "Not available" : `${percentFormatter.format(value)}%`;
}

export default function ProfitMarginCalculator() {
  const [costInput, setCostInput] = useState("");
  const [sellingPriceInput, setSellingPriceInput] = useState("");

  const costError = validateAmount(costInput, "Cost price");
  const sellingPriceError = validateAmount(sellingPriceInput, "Selling price");
  const calculation = useMemo<ProfitMarginCalculation | null>(() => {
    if (costError || sellingPriceError || costInput.trim() === "" || sellingPriceInput.trim() === "") return null;
    return calculateProfitMargin(Number(costInput), Number(sellingPriceInput));
  }, [costError, sellingPriceError, costInput, sellingPriceInput]);

  function reset() {
    setCostInput("");
    setSellingPriceInput("");
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]">
      <form className="lt-card" onSubmit={(event) => event.preventDefault()} noValidate>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="lt-eyebrow">Inputs</p>
            <h2 className="lt-heading-2 mt-2">Enter your numbers</h2>
          </div>
          <button type="button" onClick={reset} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Reset calculator">
            <RotateCcw size={15} />
            Reset
          </button>
        </div>

        <div className="mt-8 space-y-6">
          <div>
            <label htmlFor="cost-price" className="lt-label mb-2 block">Cost price</label>
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">₹</span>
              <input
                id="cost-price"
                className="lt-input pl-8"
                type="text"
                inputMode="decimal"
                value={costInput}
                onChange={(event) => setCostInput(event.target.value)}
                placeholder="0.00"
                aria-invalid={Boolean(costError)}
                aria-describedby={costError ? "cost-price-error" : "cost-price-help"}
              />
            </div>
            <p id="cost-price-help" className="mt-1.5 text-xs text-[var(--text-muted)]">What you spend or make the product or service for.</p>
            {costError && <p id="cost-price-error" className="mt-1.5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{costError}</p>}
          </div>

          <div>
            <label htmlFor="selling-price" className="lt-label mb-2 block">Selling price</label>
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">₹</span>
              <input
                id="selling-price"
                className="lt-input pl-8"
                type="text"
                inputMode="decimal"
                value={sellingPriceInput}
                onChange={(event) => setSellingPriceInput(event.target.value)}
                placeholder="0.00"
                aria-invalid={Boolean(sellingPriceError)}
                aria-describedby={sellingPriceError ? "selling-price-error" : "selling-price-help"}
              />
            </div>
            <p id="selling-price-help" className="mt-1.5 text-xs text-[var(--text-muted)]">What your customer pays.</p>
            {sellingPriceError && <p id="selling-price-error" className="mt-1.5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{sellingPriceError}</p>}
          </div>
        </div>
      </form>

      <section className="lt-card" aria-live="polite" aria-label="Profit margin results">
        <p className="lt-eyebrow">Your result</p>
        {calculation ? <Results calculation={calculation} /> : (
          <div className="flex min-h-64 items-center justify-center py-10 text-center">
            <p className="max-w-xs text-sm leading-relaxed text-[var(--text-secondary)]">Enter a cost price and selling price to see your profit, margin and markup.</p>
          </div>
        )}
      </section>
    </div>
  );
}

function Results({ calculation }: { calculation: ProfitMarginCalculation }) {
  const statusCopy = {
    profit: "Profit",
    "break-even": "Break-even",
    loss: "Loss",
  }[calculation.status];
  const statusClass = calculation.status === "profit" ? "text-[var(--lt-success)]" : calculation.status === "loss" ? "text-[var(--lt-accent-dark)]" : "text-[var(--text-secondary)]";

  return (
    <div className="mt-6">
      <div className="border-b border-[var(--border)] pb-6">
        <p className="text-sm font-semibold text-[var(--text-secondary)]">Profit margin</p>
        <p className="mt-2 break-words text-4xl font-black text-[var(--lt-primary)]">{formatPercent(calculation.margin)}</p>
        <p className={`mt-3 text-sm font-bold ${statusClass}`}>Status: {statusCopy}</p>
      </div>
      <div className="grid gap-3 pt-6 sm:grid-cols-2">
        <ResultItem label="Profit" value={formatCurrency(calculation.profit)} />
        <ResultItem label="Markup" value={formatPercent(calculation.markup)} />
      </div>
      {(calculation.margin === null || calculation.markup === null) && <p className="mt-5 text-xs leading-relaxed text-[var(--text-muted)]">A percentage is not available when its denominator is ₹0.</p>}
    </div>
  );
}

function ResultItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 break-words text-xl font-bold text-[var(--text-primary)]">{value}</p>
    </div>
  );
}
