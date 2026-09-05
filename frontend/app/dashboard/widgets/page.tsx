"use client";

import { Check, Copy, Loader2, Plus, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import LiveProofPreview from "@/components/saas/LiveProofPreview";
import { useAuth } from "@/hooks/useAuth";
import { createWidget, deactivateWidget, getWidgets, updateWidget, type Widget, type WidgetDraft } from "@/services/saas.service";

const emptyDraft: WidgetDraft = { name: "My first widget", domain_name: "example.com", theme_color: "#f97316", position: "bottom-left", display_delay: 3, is_active: true };

export default function WidgetsPage() {
  const { accessToken } = useAuth();
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState<WidgetDraft>(emptyDraft);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const selected = useMemo(() => widgets.find((widget) => widget.id === selectedId) ?? null, [selectedId, widgets]);
  const embedCode = selected ? `<script src="https://letrusto.com/widget.js" data-id="${selected.id}" async></script>` : "";

  useEffect(() => {
    if (!accessToken) return;
    getWidgets(accessToken).then((items) => {
      setWidgets(items);
      if (items[0]) { setSelectedId(items[0].id); setDraft(toDraft(items[0])); }
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Could not load widgets.")).finally(() => setLoading(false));
  }, [accessToken]);

  function selectWidget(widget: Widget) { setSelectedId(widget.id); setDraft(toDraft(widget)); setError(""); }
  function startNew() { setSelectedId(null); setDraft(emptyDraft); setError(""); }
  function setField<K extends keyof WidgetDraft>(field: K, value: WidgetDraft[K]) { setDraft((current) => ({ ...current, [field]: value })); }

  async function save() {
    if (!accessToken) return;
    setSaving(true); setError("");
    try {
      const saved = selectedId ? await updateWidget(accessToken, selectedId, draft) : await createWidget(accessToken, draft);
      setWidgets((current) => selectedId ? current.map((item) => item.id === saved.id ? saved : item) : [saved, ...current]);
      setSelectedId(saved.id); setDraft(toDraft(saved));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save widget."); }
    finally { setSaving(false); }
  }

  async function remove() {
    if (!accessToken || !selected) return;
    if (!window.confirm("Deactivate this widget? Its events will remain stored.")) return;
    try { const updated = await deactivateWidget(accessToken, selected.id); setWidgets((current) => current.map((item) => item.id === updated.id ? updated : item)); setDraft(toDraft(updated)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not deactivate widget."); }
  }

  async function copyCode() { if (!embedCode) return; await navigator.clipboard.writeText(embedCode); setCopied(true); window.setTimeout(() => setCopied(false), 1600); }

  if (loading) return <div className="flex min-h-[50vh] items-center justify-center text-sm text-[#587268]"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading widgets</div>;
  return (
    <div>
      <header className="flex flex-col justify-between gap-5 border-b border-[#d9e5df] pb-7 sm:flex-row sm:items-end"><div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#e11d48]">Widget management</p><h2 className="mt-2 text-3xl font-black tracking-tight">Make trust visible.</h2><p className="mt-2 max-w-xl text-sm leading-6 text-[#587268]">Tune the moment a new visitor sees your customers choosing you.</p></div><button type="button" onClick={startNew} className="flex items-center justify-center gap-2 bg-[#17382e] px-4 py-3 text-sm font-bold text-white hover:bg-[#0f2b23]"><Plus className="h-4 w-4" /> New widget</button></header>
      {error && <p className="mt-5 border border-[#f6c5cf] bg-[#fff4f5] px-4 py-3 text-sm text-[#a31835]" role="alert">{error}</p>}
      <div className="mt-8 grid gap-6 xl:grid-cols-[220px_minmax(0,1fr)_minmax(280px,0.75fr)]">
        <section><div className="mb-3 flex items-center justify-between"><h3 className="text-xs font-bold uppercase tracking-[0.16em] text-[#71877f]">Your widgets</h3><span className="text-xs text-[#71877f]">{widgets.length}</span></div><div className="space-y-2">{widgets.map((widget) => <button type="button" key={widget.id} onClick={() => selectWidget(widget)} className={`w-full border p-3 text-left ${selectedId === widget.id ? "border-[#17382e] bg-white" : "border-transparent bg-[#e8f0ec] hover:border-[#b9cec2]"}`}><span className="block truncate text-sm font-bold">{widget.name}</span><span className="mt-1 block truncate text-xs text-[#71877f]">{widget.domain_name}</span><span className={`mt-2 inline-block text-[10px] font-bold uppercase tracking-widest ${widget.is_active ? "text-[#0f766e]" : "text-[#a31835]"}`}>{widget.is_active ? "Live" : "Paused"}</span></button>)}{widgets.length === 0 && <p className="border border-dashed border-[#b9cec2] p-4 text-xs leading-5 text-[#71877f]">Create your first widget to start collecting proof.</p>}</div></section>
        <section className="border border-[#d9e5df] bg-[#fbfdfc] p-5 sm:p-7"><div className="flex items-center justify-between"><div><h3 className="text-lg font-black">{selected ? "Widget settings" : "Create a widget"}</h3><p className="mt-1 text-xs text-[#71877f]">Changes appear in the preview instantly.</p></div>{selected && <button type="button" onClick={remove} className="flex items-center gap-1 text-xs font-bold text-[#a31835] hover:text-[#be123c]"><Trash2 className="h-3.5 w-3.5" /> Deactivate</button>}</div><div className="mt-7 grid gap-5 sm:grid-cols-2"><label className="sm:col-span-2"><span className="label">Widget name</span><input className="input" value={draft.name} onChange={(event) => setField("name", event.target.value)} /></label><label className="sm:col-span-2"><span className="label">Allowed domain</span><input className="input" value={draft.domain_name} onChange={(event) => setField("domain_name", event.target.value)} placeholder="yoursite.com" /></label><label><span className="label">Theme color</span><div className="flex gap-2"><input className="h-11 w-14 cursor-pointer border border-[#d9e5df] bg-white p-1" type="color" value={draft.theme_color} onChange={(event) => setField("theme_color", event.target.value)} /><input className="input" value={draft.theme_color} onChange={(event) => setField("theme_color", event.target.value)} /></div></label><label><span className="label">Popup position</span><select className="input" value={draft.position} onChange={(event) => setField("position", event.target.value as WidgetDraft["position"])}><option value="bottom-left">Bottom left</option><option value="bottom-right">Bottom right</option><option value="top-left">Top left</option><option value="top-right">Top right</option></select></label><label><span className="label">Display delay (seconds)</span><input className="input" type="number" min="1" max="3600" value={draft.display_delay} onChange={(event) => setField("display_delay", Number(event.target.value))} /></label></div><button type="button" onClick={save} disabled={saving} className="mt-7 flex items-center gap-2 bg-[#e11d48] px-4 py-3 text-sm font-bold text-white hover:bg-[#be123c] disabled:opacity-60">{saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />} {selected ? "Save settings" : "Create widget"}</button></section>
        <aside className="space-y-5"><div><p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-[#71877f]">Live preview</p><LiveProofPreview color={draft.theme_color} compact /></div><div className="border border-[#d9e5df] bg-white p-4"><div className="flex items-center justify-between gap-3"><div><h3 className="text-sm font-black">Embed code</h3><p className="mt-1 text-xs text-[#71877f]">Paste before the closing body tag.</p></div><button type="button" onClick={copyCode} disabled={!embedCode} className="flex items-center gap-1 text-xs font-bold text-[#e11d48] disabled:opacity-40">{copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}{copied ? "Copied" : "Copy"}</button></div><code className="mt-4 block overflow-x-auto bg-[#17382e] p-3 text-[11px] leading-5 text-[#e8f0ec]">{embedCode || "Create a widget to generate your embed code."}</code></div></aside>
      </div>
      <style jsx>{`.label{display:block;margin-bottom:.5rem;font-size:.75rem;font-weight:700;color:#587268}.input{width:100%;border:1px solid #d9e5df;background:#fff;padding:.7rem .8rem;font-size:.875rem;color:#17382e;outline:none}.input:focus{border-color:#e11d48;box-shadow:0 0 0 3px #fce7eb}`}</style>
    </div>
  );
}

function toDraft(widget: Widget): WidgetDraft { return { name: widget.name, domain_name: widget.domain_name, theme_color: widget.theme_color, position: widget.position, display_delay: widget.display_delay, is_active: widget.is_active }; }
