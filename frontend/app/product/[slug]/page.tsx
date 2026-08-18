import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPublicProduct, getPublicProducts, toCommerceProduct } from "@/services/product.service";
import ProductDetailView from "./ProductDetailView";

type Props = {
  params: Promise<{ slug: string }>;
};

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
    description: product.description,
    openGraph: {
      title: `${product.name} | LeTrusto`,
      description: product.description,
      images: product.images,
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
