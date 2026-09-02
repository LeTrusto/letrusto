import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SchemaOrg from "@/components/SchemaOrg";
import { SERVICES, getServiceBySlug } from "@/lib/services";

type Props = { params: Promise<{ slug: string }> };
export function generateStaticParams() { return SERVICES.filter((service) => service.status === "published").map((service) => ({ slug: service.slug })); }
export async function generateMetadata({ params }: Props): Promise<Metadata> { const service = getServiceBySlug((await params).slug); return service ? { title: service.seo.title, description: service.seo.description, alternates: { canonical: `/services/${service.slug}` }, openGraph: { title: `${service.seo.title} | LeTrusto`, description: service.seo.description, url: `/services/${service.slug}`, siteName: "LeTrusto", type: "website" } } : { title: "Service" }; }

export default async function ServiceDetailPage({ params }: Props) {
  const service = getServiceBySlug((await params).slug);
  if (!service) notFound();
  return <main className="mx-auto max-w-5xl px-4 py-12 md:px-6 md:py-20"><SchemaOrg type="WebPage" data={{ name: service.name, url: `/services/${service.slug}`, description: service.seo.description }} /><Link href="/services" className="text-sm font-semibold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">&larr; All services</Link><div className="mt-10 max-w-3xl"><p className="lt-eyebrow">{service.category}</p><h1 className="lt-heading-1 mt-3">{service.name}</h1><p className="mt-5 text-xl leading-8 text-[var(--text-secondary)]">{service.description}</p><Link href={`/services/quote?service=${service.slug}`} className="lt-btn lt-btn-lg lt-btn-primary mt-8">Get a quote</Link></div><div className="mt-14 grid gap-10 border-t border-[var(--border)] pt-12 md:grid-cols-2"><Section title="The problem it solves" items={[service.problem]} /><Section title="Typical use" items={[service.useCase]} /><Section title="What is included" items={service.included} /><Section title="What is not included" items={service.exclusions} /><Section title="Typical process" items={service.process} numbered /><Section title="What we need from you" items={service.informationNeeded} /></div><div className="mt-14 border-t border-[var(--border)] pt-10"><p className="text-sm leading-6 text-[var(--text-secondary)]">{service.pricing.notes}</p><Link href={`/services/quote?service=${service.slug}`} className="lt-btn lt-btn-md lt-btn-secondary mt-5">Discuss this service</Link></div></main>;
}

function Section({ title, items, numbered = false }: { title: string; items: string[]; numbered?: boolean }) { const List = numbered ? "ol" : "ul"; return <section><h2 className="lt-heading-2">{title}</h2><List className={`${numbered ? "list-decimal pl-5" : ""} mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]`}>{items.map((item) => <li key={item}>{item}</li>)}</List></section>; }