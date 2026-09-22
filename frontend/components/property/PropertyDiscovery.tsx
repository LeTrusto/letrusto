"use client";

import { ArrowLeft, ArrowRight, RotateCcw, Search, SlidersHorizontal } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { getPublicLocations, getPublicProperties, type PublicLocation, type PublicPropertyPage } from "@/services/property.service";
import { PropertyCard } from "./PropertyCard";

const propertyTypes = [{ value: "APARTMENT", label: "Apartment" }, { value: "INDEPENDENT_HOUSE", label: "Independent house" }, { value: "VILLA", label: "Villa" }, { value: "RESIDENTIAL_PLOT", label: "Plot" }];
function queryValue(params: URLSearchParams, key: string): string {
  return params.get(key) ?? "";
}

export function PropertyDiscovery() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.toString();
  const [data, setData] = useState<PublicPropertyPage | null>(null);
  const [loadedQuery, setLoadedQuery] = useState<string | null>(null);
  const [locations, setLocations] = useState<PublicLocation[]>([]);
  const [error, setError] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const params = useMemo(() => new URLSearchParams(query), [query]);
  const search = queryValue(params, "search");

  useEffect(() => {
    let cancelled = false;
    void getPublicLocations().then((items) => { if (!cancelled) setLocations(items.filter((location) => location.location_type === "LOCALITY")); }).catch(() => undefined);
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const request = {
      page: Number(queryValue(params, "page") || 1),
      page_size: 12,
      type: queryValue(params, "type") || undefined,
      bhk: queryValue(params, "bhk") ? Number(queryValue(params, "bhk")) : undefined,
      min_price: queryValue(params, "min_price") ? Number(queryValue(params, "min_price")) : undefined,
      max_price: queryValue(params, "max_price") ? Number(queryValue(params, "max_price")) : undefined,
      locality: queryValue(params, "locality") || undefined,
      search: search || undefined,
      sort: (queryValue(params, "sort") || "newest") as "newest" | "price_asc" | "price_desc",
    };
    void getPublicProperties(request).then((result) => { if (!cancelled) { setData(result); setLoadedQuery(query); setError(false); } }).catch(() => { if (!cancelled) { setLoadedQuery(query); setError(true); } });
    return () => { cancelled = true; };
  }, [params, search, query]);

  function update(values: Record<string, string | undefined>) {
    const next = new URLSearchParams(params);
    Object.entries(values).forEach(([key, value]) => value ? next.set(key, value) : next.delete(key));
    next.delete("page");
    router.push(next.toString() ? `/properties?${next}` : "/properties");
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = new FormData(event.currentTarget).get("search")?.toString().trim() ?? "";
    update({ search: value });
  }

  function clearFilters() {
    router.push("/properties");
  }

  const page = data?.page ?? Number(queryValue(params, "page") || 1);
  const hasFilters = ["type", "bhk", "min_price", "max_price", "locality", "search", "sort"].some((key) => params.has(key));

  return <main className="collection-page discovery-page">
    <nav className="site-nav collection-nav section-shell"><Link href="/" className="temporary-mark"><span className="mark-dot" />BENGALURU PROPERTY</Link><div className="nav-links"><Link href="/">Home</Link><span className="nav-current">Discover</span><Link href="/login">For sellers</Link></div><Link href="/" className="nav-pill"><ArrowLeft size={15} /> Home</Link></nav>
    <header className="collection-header section-shell"><div><p className="eyebrow">Bangalore / Real property discovery</p><h1 className="display-title">Places with<br /><em>a point of view.</em></h1></div><p className="collection-intro">Live properties, presented with the details that help you decide where to look next.</p></header>
    <section className="discovery-controls section-shell" aria-label="Property discovery filters">
      <form className="discovery-search" onSubmit={submitSearch}><Search size={18} aria-hidden="true" /><input name="search" defaultValue={search} placeholder="Search homes, neighbourhoods or localities" aria-label="Search properties" /><button type="submit" className="button button-dark">Search</button></form>
      <button type="button" className="discovery-filter-toggle" onClick={() => setFiltersOpen((open) => !open)} aria-expanded={filtersOpen}><SlidersHorizontal size={16} /> Filters</button>
      <div className={`discovery-filter-grid ${filtersOpen ? "is-open" : ""}`}>
        <label>Property type<select value={queryValue(params, "type")} onChange={(event) => update({ type: event.target.value })}><option value="">All types</option>{propertyTypes.map((item) => <option value={item.value} key={item.value}>{item.label}</option>)}</select></label>
        <label>BHK<select value={queryValue(params, "bhk")} onChange={(event) => update({ bhk: event.target.value })}><option value="">Any bedrooms</option><option value="1">1 BHK</option><option value="2">2 BHK</option><option value="3">3 BHK</option><option value="4">4+ BHK</option></select></label>
        <label>Locality<select value={queryValue(params, "locality")} onChange={(event) => update({ locality: event.target.value })}><option value="">All Bengaluru</option>{locations.map((location) => <option value={location.slug} key={location.id}>{location.name}</option>)}</select></label>
        <label>Minimum price<input inputMode="numeric" value={queryValue(params, "min_price")} onChange={(event) => update({ min_price: event.target.value.replace(/[^0-9]/g, "") })} placeholder="INR" /></label>
        <label>Maximum price<input inputMode="numeric" value={queryValue(params, "max_price")} onChange={(event) => update({ max_price: event.target.value.replace(/[^0-9]/g, "") })} placeholder="INR" /></label>
        <label>Sort<select value={queryValue(params, "sort") || "newest"} onChange={(event) => update({ sort: event.target.value })}><option value="newest">Newest</option><option value="price_asc">Price: low to high</option><option value="price_desc">Price: high to low</option></select></label>
      </div>
      {hasFilters && <button type="button" className="discovery-clear" onClick={clearFilters}><RotateCcw size={14} /> Clear filters</button>}
    </section>
    <div className="collection-filter-bar section-shell"><span>{data ? `${data.total} ${data.total === 1 ? "place" : "places"} across Bengaluru` : "Finding live properties across Bengaluru"}</span><span>One city / many ways to live <ArrowRight size={14} /></span></div>
    <section className="collection-grid section-shell" aria-live="polite">
      {!data && !error && Array.from({ length: 4 }, (_, index) => <div className="property-card discovery-skeleton" key={index} aria-hidden="true"><div className="discovery-skeleton-image" /><div className="discovery-skeleton-line" /><div className="discovery-skeleton-line short" /></div>)}
      {error && loadedQuery === query && <div className="discovery-state"><p className="eyebrow">A brief pause</p><h2>Property discovery is temporarily unavailable.</h2><p>We couldn&apos;t reach the live property collection.</p><button type="button" className="button button-dark" onClick={() => router.refresh()}>Try again <RotateCcw size={15} /></button></div>}
      {loadedQuery === query && data && !data.items.length && <div className="discovery-state"><p className="eyebrow">Nothing here yet</p><h2>{hasFilters ? "No properties match these filters." : "New properties are being added."}</h2><p>Try a different neighbourhood or clear the filters to browse the full collection.</p>{hasFilters && <button type="button" className="button button-dark" onClick={clearFilters}>Browse all properties</button>}</div>}
      {loadedQuery === query && data?.items.map((property, index) => <PropertyCard key={property.id} property={property} featured={index === 0} />)}
    </section>
    {loadedQuery === query && data && data.total > data.page_size && <nav className="discovery-pagination section-shell" aria-label="Property pages"><button type="button" disabled={page <= 1} onClick={() => { const next = new URLSearchParams(params); next.set("page", String(page - 1)); router.push(`/properties?${next}`); }}><ArrowLeft size={15} /> Previous</button><span>Page {data.page} of {Math.ceil(data.total / data.page_size)}</span><button type="button" disabled={!data.has_more} onClick={() => { const next = new URLSearchParams(params); next.set("page", String(page + 1)); router.push(`/properties?${next}`); }}>Next <ArrowRight size={15} /></button></nav>}
    <footer className="collection-footer section-shell"><Link href="/" className="text-link"><ArrowLeft size={16} /> Back to the journal</Link><span>More places are on their way.</span></footer>
  </main>;
}