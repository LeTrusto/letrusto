type SchemaOrgProps = {
  type: "WebSite" | "Product" | "BreadcrumbList" | "Organization";
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
