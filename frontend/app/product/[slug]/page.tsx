import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPublicProduct, getPublicProducts, toCommerceProduct } from "@/services/product.service";
import ProductDetailView from "./ProductDetailView";

type Props = {
  params: Promise<{ slug: string }>;
};

function plainText(value: string) {
  return value.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

export async function generateStaticParams() {
  return [];
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  let product;
  try {
    product = toCommerceProduct(await getPublicProduct(slug));
  } catch {
    return { title: "Product Not Found" };
  }

  return {
    title: product.name,
    description: plainText(product.description).slice(0, 160),
    alternates: { canonical: `/product/${product.slug}` },
    openGraph: {
      title: `${product.name} | LeTrusto`,
      description: plainText(product.description).slice(0, 160),
      url: `/product/${product.slug}`,
      siteName: "LeTrusto",
      type: "website",
      images: product.images.slice(0, 1).map((url) => ({ url })),
    },
    twitter: {
      card: "summary_large_image",
      title: `${product.name} | LeTrusto`,
      description: plainText(product.description).slice(0, 160),
      images: product.images.slice(0, 1),
    },
  };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  let product;
  try {
    product = toCommerceProduct(await getPublicProduct(slug));
  } catch {
    notFound();
  }

  const related = (await getPublicProducts()).map(toCommerceProduct)
    .filter((p) => p.category === product.category && p.id !== product.id).slice(0, 4);

  return <ProductDetailView product={product} related={related} />;
}
