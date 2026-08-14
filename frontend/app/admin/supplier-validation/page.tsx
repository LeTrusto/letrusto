import type { Metadata } from "next";
import SupplierValidationView from "./SupplierValidationView";

export const metadata: Metadata = {
  title: "Supplier Validation",
  robots: { index: false, follow: false },
};

export default function SupplierValidationPage() {
  return <SupplierValidationView />;
}
