import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getMockProduct, MOCK_PRODUCTS } from "@/lib/mockData";
import ProductDetailView from "./ProductDetailView";

type Props = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return MOCK_PRODUCTS.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const product = getMockProduct(slug);
  if (!product) return { title: "Product Not Found" };

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
  const product = getMockProduct(slug);
  if (!product) notFound();

  const related = MOCK_PRODUCTS.filter(
    (p) => p.category === product.category && p.id !== product.id
  ).slice(0, 4);

  return <ProductDetailView product={product} related={related} />;
}
