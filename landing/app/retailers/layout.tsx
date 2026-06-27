import type { Metadata } from "next";
import { MARKET_STATS } from "@/lib/marketStats";
import RetailersJsonLd from "./RetailersJsonLd";

export const metadata: Metadata = {
  title: "List Your Store — Free GEO for AI Agents (VTEX, Shopify, Magento, WooCommerce)",
  description:
    `List your store on CLI Market for free. VTEX, Shopify, Magento, or WooCommerce. 30 seconds, zero code. Your products visible in AI agent searches via MCP tools and commerce API. ${MARKET_STATS.retailersPhraseEn}, ${MARKET_STATS.pricesVerifiedLabel} verified price data points.`,
  keywords: [
    "GEO generative engine optimization",
    "list store AI agents",
    "VTEX API integration",
    "WooCommerce Store API",
    "API tools for e-commerce",
    "AI commerce API",
  ],
  alternates: {
    canonical: "/retailers",
  },
  openGraph: {
    title: "CLI Market for Retailers — Your brand inside AI agents",
    description:
      "Free listing for VTEX, Shopify, Magento, WooCommerce. 30 seconds. AI agents discover and compare your products.",
    url: "https://cli-market.dev/retailers",
    type: "website",
  },
};

export default function RetailersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <RetailersJsonLd />
      {children}
    </>
  );
}
