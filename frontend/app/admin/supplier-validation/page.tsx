import type { Metadata } from "next";
import SupplierValidationView from "./SupplierValidationView";

export const metadata: Metadata = {
  title: "Product Discovery & Selection",
  robots: { index: false, follow: false },
};

export default function SupplierValidationPage() {
  return <SupplierValidationView />;
}
