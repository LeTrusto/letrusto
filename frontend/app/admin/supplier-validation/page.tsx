import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Product Discovery & Selection",
  robots: { index: false, follow: false },
};

export default function SupplierValidationPage() {
  redirect("/admin/products");
}
