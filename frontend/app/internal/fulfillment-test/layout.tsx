import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Internal Fulfillment Test",
  robots: {
    index: false,
    follow: false,
    noarchive: true,
  },
};

export default function FulfillmentTestLayout({ children }: Readonly<{ children: ReactNode }>) {
  return children;
}