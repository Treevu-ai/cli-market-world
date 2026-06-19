import type { Metadata } from "next";
import ProductArchitecturePage from "@/components/ProductArchitecturePage";

export const metadata: Metadata = {
  title: "Product",
  description: "CLI Market architecture: data ingestion, normalization, intelligence, and commerce workflows across 80+ LATAM retailers.",
  alternates: { canonical: "/product" },
  openGraph: {
    title: "Product Architecture — CLI Market",
    description: "How CLI Market ingests, normalizes, and delivers retail intelligence across Latin America.",
  },
};

export default function ProductPage() {
  return <ProductArchitecturePage />;
}
