"use client";

import { useMemo, useRef, useState } from "react";
import { Plus, Printer, RotateCcw, Trash2 } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import { calculateInvoice, validateInvoiceItem, validateInvoiceItems, type DiscountType, type InvoiceCalculation, type InvoiceItem } from "@/lib/invoiceCalculator";

const currencyFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
const today = new Date().toISOString().slice(0, 10);

function newItem(): InvoiceItem {
  return { id: `${Date.now()}-${Math.random()}`, description: "", quantity: 1, unitPrice: 0 };
}

function defaultInvoiceNumber() {
  return `INV-${today.replaceAll("-", "")}`;
}

function formatCurrency(value: number) {
  return Number.isFinite(value) ? `₹${currencyFormatter.format(value)}` : "Not available";
}

function displayDate(value: string) {
  if (!value) return "-";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

type PartyDetails = {
  name: string;
  address: string;
  phone: string;
  email: string;
  gstin: string;
  website?: string;
};

const emptyParty: PartyDetails = { name: "", address: "", phone: "", email: "", gstin: "" };

export default function InvoiceGenerator() {
  const completionTracked = useRef(false);
  const [seller, setSeller] = useState<PartyDetails>({ ...emptyParty });
  const [customer, setCustomer] = useState<PartyDetails>({ ...emptyParty });
  const [invoiceNumber, setInvoiceNumber] = useState(defaultInvoiceNumber);
  const [invoiceDate, setInvoiceDate] = useState(today);
  const [dueDate, setDueDate] = useState("");
  const [items, setItems] = useState<InvoiceItem[]>([newItem()]);
  const [discountType, setDiscountType] = useState<DiscountType>("percentage");
  const [discountInput, setDiscountInput] = useState("0");
  const [taxEnabled, setTaxEnabled] = useState(false);
  const [taxInput, setTaxInput] = useState("0");
  const [notes, setNotes] = useState("");
  const [paymentInfo, setPaymentInfo] = useState("");

  const discountValue = Number(discountInput);
  const taxRate = taxEnabled ? Number(taxInput) : 0;
  const itemError = validateInvoiceItems(items);
  const invoiceError = !invoiceNumber.trim() ? "Invoice number is required." : !invoiceDate ? "Invoice date is required." : dueDate && dueDate < invoiceDate ? "Due date cannot be before the invoice date." : null;
  const calculation = useMemo<InvoiceCalculation | null>(() => {
    if (itemError || invoiceError || !Number.isFinite(discountValue) || !Number.isFinite(taxRate)) return null;
    try {
      return calculateInvoice(items, discountType, discountValue, taxRate);
    } catch {
      return null;
    }
  }, [discountType, discountValue, invoiceError, itemError, items, taxRate]);

  const calculationError = itemError || invoiceError || (
    !Number.isFinite(discountValue) || discountValue < 0 ? "Discount must be zero or greater." :
      discountType === "percentage" && discountValue > 100 ? "Percentage discount cannot exceed 100%." :
        !Number.isFinite(taxRate) || taxRate < 0 || taxRate > 100 ? "Tax rate must be between 0% and 100%." :
          calculation === null ? "Discount cannot be greater than the subtotal." : null
  );

  function updateItem(id: string, field: keyof InvoiceItem, value: string) {
    setItems((current) => current.map((item) => item.id === id ? { ...item, [field]: field === "description" ? value : Number(value) } : item));
  }

  function reset() {
    setSeller({ ...emptyParty });
    setCustomer({ ...emptyParty });
    setInvoiceNumber(defaultInvoiceNumber());
    setInvoiceDate(today);
    setDueDate("");
    setItems([newItem()]);
    setDiscountType("percentage");
    setDiscountInput("0");
    setTaxEnabled(false);
    setTaxInput("0");
    setNotes("");
    setPaymentInfo("");
  }

  function printInvoice() {
    if (calculation) {
      if (!completionTracked.current) {
        trackSafeEvent("tool_complete", { tool_name: "invoice-generator" });
        completionTracked.current = true;
      }
      window.print();
    }
  }

  return (
    <div className="invoice-tool-page">
      <div className="invoice-tool-controls space-y-8">
        <section className="lt-card">
          <div className="flex items-start justify-between gap-4">
            <div><p className="lt-eyebrow">Step 1</p><h2 className="lt-heading-2 mt-2">Your details</h2></div>
            <button type="button" onClick={reset} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Start a new invoice"><RotateCcw size={15} /> New invoice</button>
          </div>
          <div className="mt-7 grid gap-5 md:grid-cols-2">
            <PartyFields legend="Seller / business" party={seller} setParty={setSeller} includeWebsite />
            <PartyFields legend="Customer" party={customer} setParty={setCustomer} />
          </div>
          <div className="mt-7 border-t border-[var(--border)] pt-7">
            <p className="lt-eyebrow">Invoice details</p>
            <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <Field label="Invoice number" id="invoice-number" value={invoiceNumber} onChange={setInvoiceNumber} required />
              <Field label="Invoice date" id="invoice-date" type="date" value={invoiceDate} onChange={setInvoiceDate} required />
              <Field label="Due date (optional)" id="due-date" type="date" value={dueDate} onChange={setDueDate} />
              <div><span className="lt-label mb-2 block">Currency</span><div className="lt-input bg-[var(--surface-soft)]">INR (₹)</div></div>
            </div>
            {invoiceError && <p className="mt-3 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{invoiceError}</p>}
          </div>
        </section>

        <section className="lt-card">
          <div><p className="lt-eyebrow">Step 2</p><h2 className="lt-heading-2 mt-2">Items or services</h2></div>
          <div className="mt-6 space-y-4">
            {items.map((item, index) => {
              const error = validateInvoiceItem(item);
              return <div key={item.id} className="border border-[var(--border)] bg-[var(--surface-soft)] p-4">
                <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_100px_140px_32px] sm:items-end">
                  <Field label={`Description ${index + 1}`} id={`item-description-${item.id}`} value={item.description} onChange={(value) => updateItem(item.id, "description", value)} placeholder="Product or service" />
                  <Field label="Quantity" id={`item-quantity-${item.id}`} type="number" inputMode="decimal" min="0" step="any" value={String(item.quantity)} onChange={(value) => updateItem(item.id, "quantity", value)} />
                  <Field label="Unit price (₹)" id={`item-price-${item.id}`} type="number" inputMode="decimal" min="0" step="any" value={String(item.unitPrice)} onChange={(value) => updateItem(item.id, "unitPrice", value)} />
                  <button type="button" onClick={() => setItems((current) => current.filter((currentItem) => currentItem.id !== item.id))} className="flex h-10 w-10 items-center justify-center text-[var(--text-secondary)] hover:text-[var(--lt-accent-dark)]" aria-label={`Remove item ${index + 1}`}><Trash2 size={18} /></button>
                </div>
                <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm"><span className="text-[var(--text-muted)]">Line total</span><strong>{formatCurrency(item.quantity * item.unitPrice || 0)}</strong></div>
                {error && <p className="mt-2 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{error}</p>}
              </div>;
            })}
          </div>
          <button type="button" onClick={() => setItems((current) => [...current, newItem()])} className="lt-btn lt-btn-sm lt-btn-secondary mt-5"><Plus size={16} /> Add item</button>
        </section>

        <section className="lt-card">
          <div><p className="lt-eyebrow">Step 3</p><h2 className="lt-heading-2 mt-2">Adjust totals</h2></div>
          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            <div>
              <label htmlFor="discount-type" className="lt-label mb-2 block">Discount</label>
              <div className="flex gap-2"><select id="discount-type" className="lt-select w-36" value={discountType} onChange={(event) => setDiscountType(event.target.value as DiscountType)}><option value="percentage">Percentage</option><option value="fixed">Fixed amount</option></select><input aria-label="Discount value" className="lt-input" type="number" min="0" step="any" value={discountInput} onChange={(event) => setDiscountInput(event.target.value)} /></div>
            </div>
            <div>
              <label htmlFor="tax-enabled" className="flex min-h-10 items-center gap-3 text-sm font-semibold text-[var(--text-primary)]"><input id="tax-enabled" type="checkbox" checked={taxEnabled} onChange={(event) => setTaxEnabled(event.target.checked)} className="h-4 w-4 accent-[var(--lt-primary)]" />Apply tax / GST</label>
              {taxEnabled && <div className="mt-2 flex items-center gap-2"><input id="tax-rate" aria-label="Tax percentage" className="lt-input max-w-40" type="number" min="0" max="100" step="any" value={taxInput} onChange={(event) => setTaxInput(event.target.value)} /><span className="text-sm font-semibold">%</span></div>}
            </div>
          </div>
          {calculationError && <p className="mt-4 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{calculationError}</p>}
          <div className="mt-7 grid gap-5 sm:grid-cols-2"><TextArea label="Notes" id="invoice-notes" value={notes} onChange={setNotes} placeholder="Optional notes or terms" /><TextArea label="Payment information" id="payment-information" value={paymentInfo} onChange={setPaymentInfo} placeholder="Optional UPI, bank details or payment instructions" /></div>
        </section>
      </div>

      <section className="mt-10">
        <div className="invoice-tool-controls mb-5 flex flex-wrap items-center justify-between gap-4"><div><p className="lt-eyebrow">Step 4</p><h2 className="lt-heading-2 mt-2">Review and print</h2></div><button type="button" onClick={printInvoice} disabled={!calculation} className="lt-btn lt-btn-md lt-btn-primary"><Printer size={17} /> Print invoice / Save as PDF</button></div>
        <InvoicePreview seller={seller} customer={customer} invoiceNumber={invoiceNumber} invoiceDate={invoiceDate} dueDate={dueDate} items={items} calculation={calculation} notes={notes} paymentInfo={paymentInfo} />
        <p className="invoice-tool-controls mt-4 text-xs leading-relaxed text-[var(--text-muted)]">Your invoice is created in this browser only. Review applicable tax and invoicing requirements for your situation before sending it.</p>
      </section>
    </div>
  );
}

function PartyFields({ legend, party, setParty, includeWebsite = false }: { legend: string; party: PartyDetails; setParty: React.Dispatch<React.SetStateAction<PartyDetails>>; includeWebsite?: boolean }) {
  return <fieldset><legend className="text-sm font-bold text-[var(--text-primary)]">{legend}</legend><div className="mt-4 space-y-4"><Field label="Name" id={`${legend}-name`} value={party.name} onChange={(value) => setParty((current) => ({ ...current, name: value }))} /><TextArea label="Address" id={`${legend}-address`} value={party.address} onChange={(value) => setParty((current) => ({ ...current, address: value }))} rows={2} /><div className="grid gap-4 sm:grid-cols-2"><Field label="Phone" id={`${legend}-phone`} value={party.phone} onChange={(value) => setParty((current) => ({ ...current, phone: value }))} /><Field label="Email" id={`${legend}-email`} type="email" value={party.email} onChange={(value) => setParty((current) => ({ ...current, email: value }))} /></div><div className="grid gap-4 sm:grid-cols-2"><Field label="GSTIN (optional)" id={`${legend}-gstin`} value={party.gstin} onChange={(value) => setParty((current) => ({ ...current, gstin: value }))} />{includeWebsite && <Field label="Website (optional)" id={`${legend}-website`} value={party.website ?? ""} onChange={(value) => setParty((current) => ({ ...current, website: value }))} />}</div></div></fieldset>;
}

function Field({ label, id, value, onChange, type = "text", inputMode, min, max, step, placeholder, required = false }: { label: string; id: string; value: string; onChange: (value: string) => void; type?: string; inputMode?: "decimal" | "email" | "tel"; min?: string; max?: string; step?: string; placeholder?: string; required?: boolean }) {
  return <div><label htmlFor={id} className="lt-label mb-2 block">{label}{required && <span aria-hidden="true"> *</span>}</label><input id={id} className="lt-input" type={type} inputMode={inputMode} min={min} max={max} step={step} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} required={required} /></div>;
}

function TextArea({ label, id, value, onChange, placeholder, rows = 3 }: { label: string; id: string; value: string; onChange: (value: string) => void; placeholder?: string; rows?: number }) {
  return <div><label htmlFor={id} className="lt-label mb-2 block">{label}</label><textarea id={id} className="lt-input min-h-20 resize-y" rows={rows} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} /></div>;
}

function InvoicePreview({ seller, customer, invoiceNumber, invoiceDate, dueDate, items, calculation, notes, paymentInfo }: { seller: PartyDetails; customer: PartyDetails; invoiceNumber: string; invoiceDate: string; dueDate: string; items: InvoiceItem[]; calculation: InvoiceCalculation | null; notes: string; paymentInfo: string }) {
  return <div className="invoice-preview mx-auto max-w-[900px] bg-white p-6 text-slate-900 shadow-[0_8px_30px_rgba(60,35,100,0.12)] sm:p-10">
    <div className="flex flex-col justify-between gap-8 border-b-2 border-slate-900 pb-8 sm:flex-row"><div><h3 className="text-2xl font-black">{seller.name || "Your business name"}</h3><PreviewText value={seller.address} /><PreviewText value={seller.phone} /><PreviewText value={seller.email} /><PreviewText value={seller.gstin ? `GSTIN: ${seller.gstin}` : ""} /></div><div className="sm:text-right"><p className="text-3xl font-black uppercase tracking-wide">Invoice</p><p className="mt-3 text-sm"><strong>No:</strong> {invoiceNumber || "-"}</p><p className="text-sm"><strong>Date:</strong> {displayDate(invoiceDate)}</p>{dueDate && <p className="text-sm"><strong>Due:</strong> {displayDate(dueDate)}</p>}</div></div>
    <div className="grid gap-6 border-b border-slate-200 py-7 sm:grid-cols-2"><div><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Bill to</p><p className="mt-2 font-bold">{customer.name || "Customer name"}</p><PreviewText value={customer.address} /><PreviewText value={customer.phone} /><PreviewText value={customer.email} /><PreviewText value={customer.gstin ? `GSTIN: ${customer.gstin}` : ""} /></div><div className="sm:text-right"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Currency</p><p className="mt-2 font-semibold">Indian Rupee (₹)</p></div></div>
    <div className="mt-7 overflow-x-auto"><table className="w-full min-w-[560px] text-left text-sm"><thead><tr className="border-b-2 border-slate-900 text-xs uppercase tracking-wider"><th className="pb-3">Description</th><th className="pb-3 text-right">Qty</th><th className="pb-3 text-right">Unit price</th><th className="pb-3 text-right">Amount</th></tr></thead><tbody>{items.map((item) => <tr key={item.id} className="border-b border-slate-200"><td className="py-4">{item.description || "-"}</td><td className="py-4 text-right">{item.quantity || 0}</td><td className="py-4 text-right">{formatCurrency(item.unitPrice || 0)}</td><td className="py-4 text-right font-semibold">{formatCurrency((item.quantity * item.unitPrice) || 0)}</td></tr>)}</tbody></table></div>
    <div className="ml-auto mt-7 w-full max-w-sm space-y-3 text-sm"><TotalRow label="Subtotal" value={calculation ? formatCurrency(calculation.subtotal) : "-"} /><TotalRow label="Discount" value={calculation ? `- ${formatCurrency(calculation.discount)}` : "-"} /><TotalRow label="Tax" value={calculation ? formatCurrency(calculation.tax) : "-"} /><div className="flex justify-between border-t-2 border-slate-900 pt-4 text-lg font-black"><span>Total</span><span>{calculation ? formatCurrency(calculation.total) : "-"}</span></div></div>
    {(notes || paymentInfo) && <div className="mt-10 grid gap-6 border-t border-slate-200 pt-6 text-sm sm:grid-cols-2"><div>{notes && <><p className="font-bold">Notes</p><p className="mt-2 whitespace-pre-wrap text-slate-600">{notes}</p></>}</div><div>{paymentInfo && <><p className="font-bold">Payment information</p><p className="mt-2 whitespace-pre-wrap text-slate-600">{paymentInfo}</p></>}</div></div>}
    <p className="mt-10 border-t border-slate-200 pt-5 text-xs text-slate-500">Please verify applicable tax and invoicing requirements for your situation.</p>
  </div>;
}

function PreviewText({ value }: { value: string }) { return value ? <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">{value}</p> : null; }
function TotalRow({ label, value }: { label: string; value: string }) { return <div className="flex justify-between gap-4"><span className="text-slate-600">{label}</span><span className="font-semibold">{value}</span></div>; }
