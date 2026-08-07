type SchemaOrgProps = {
  type: "WebSite" | "WebPage" | "Product" | "BreadcrumbList" | "FAQPage" | "Organization";
  data: Record<string, unknown>;
};

export default function SchemaOrg({ type, data }: SchemaOrgProps) {
  const schema = {
    "@context": "https://schema.org",
    "@type": type,
    ...data,
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
