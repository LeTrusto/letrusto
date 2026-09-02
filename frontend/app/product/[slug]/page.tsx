import type { Metadata } from "next";
import { notFound } from "next/navigation";

export async function generateStaticParams() {
  return [];
}

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "Product Not Found",
    robots: { index: false, follow: false },
  };
}

export default function ProductPage() {
  notFound();
}
