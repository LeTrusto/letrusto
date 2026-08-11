import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import type { AITool } from "@/types/ai-tools";

type HomeFeaturedToolsSectionProps = {
  title: string;
  subtitle?: string;
  tools: AITool[];
};

export default function HomeFeaturedToolsSection({ title, subtitle, tools }: HomeFeaturedToolsSectionProps) {
  if (tools.length === 0) return null;

  return (
    <section className="mx-auto max-w-7xl px-6 py-16">
      <div className="mb-8">
        <h2 className="lt-heading-2">{title}</h2>
        {subtitle && <p className="lt-body mt-2 max-w-2xl">{subtitle}</p>}
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {tools.map((tool) => (
          <Link
            key={tool.slug}
            href={`/ai-tools/${tool.slug}`}
            className="lt-card lt-card-hover group flex flex-col rounded-[var(--radius-xl)] p-6"
          >
            <div className="flex items-center justify-between">
              <span className="lt-badge lt-badge-brand">{tool.category.name}</span>
              <ArrowUpRight className="h-4 w-4 text-[var(--text-muted)] transition group-hover:text-[var(--lt-purple)]" />
            </div>
            <h3 className="lt-heading-3 mt-4 group-hover:text-[var(--lt-purple)]">{tool.name}</h3>
            <p className="mt-1 text-xs text-[var(--text-muted)]">{tool.provider}</p>
            <p className="lt-body-sm mt-3 line-clamp-3 flex-1">{tool.description}</p>
            {tool.bestFor.length > 0 && (
              <p className="mt-4 text-xs font-medium text-[var(--text-primary)]">
                Best for: <span className="text-[var(--text-secondary)]">{tool.bestFor[0]}</span>
              </p>
            )}
          </Link>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link href="/ai-tools" className="lt-btn lt-btn-md lt-btn-secondary">
          View all AI tools
        </Link>
        <Link href="/guides" className="lt-btn lt-btn-md lt-btn-ghost">
          Read buying guides
        </Link>
      </div>

      <p className="mt-4 text-xs text-[var(--text-muted)]">
        LeTrusto may earn a commission when you purchase through qualifying links.{" "}
        <Link href="/affiliate-disclosure" className="underline hover:text-[var(--lt-purple)]">Disclosure</Link>
      </p>
    </section>
  );
}
