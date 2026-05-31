import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "List Your Store — Free GEO for AI Agents (VTEX, Shopify, Magento)",
  description:
    "List your store on CLI Market for free. VTEX, Shopify, or Magento. 30 seconds, zero code. Your products visible in AI agent searches via MCP tools and commerce API. 60 retailers, 39K+ verified price data points.",
  keywords: [
    "GEO generative engine optimization",
    "list store AI agents",
    "VTEX API integration",
    "MCP tools for e-commerce",
    "AI commerce API",
  ],
  alternates: {
    canonical: "/retailers",
  },
  openGraph: {
    title: "CLI Market for Retailers — Your brand inside AI agents",
    description:
      "Free listing for VTEX, Shopify, Magento. 30 seconds. AI agents discover and compare your products.",
    url: "https://cli-market.dev/retailers",
    type: "website",
  },
};

export default function RetailersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
