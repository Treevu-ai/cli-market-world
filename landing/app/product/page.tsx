import type { Metadata } from "next";
import ProductArchitecturePage from "@/components/ProductArchitecturePage";
import { MARKET_STATS } from "@/lib/marketStats";

export const metadata: Metadata = {
  title: "Product",
  description: `CLI Market architecture: data ingestion, normalization, intelligence, and commerce workflows across ${MARKET_STATS.retailersDefined} LATAM retailers (${MARKET_STATS.retailersVerified} verified).`,
  alternates: { canonical: "/product" },
  openGraph: {
    title: "Product Architecture — CLI Market",
    description: "How CLI Market ingests, normalizes, and delivers retail intelligence across Latin America.",
  },
};

export default function ProductPage() {
  return <ProductArchitecturePage />;
}
