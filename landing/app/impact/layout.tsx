import type { Metadata } from "next";
import { MARKET_STATS } from "@/lib/marketStats";

export const metadata: Metadata = {
  title: "La capa programable del retail físico de LatAm",
  description: `${MARKET_STATS.pricesVerifiedLabel} verified shelf prices from ${MARKET_STATS.retailersVerified} retailers across ${MARKET_STATS.countries} countries. One API, one CLI, ${MARKET_STATS.mcpTools} API tools for AI agents.`,
  alternates: { canonical: "/impact" },
  openGraph: {
    title: "CLI Market — La capa programable del retail físico de LatAm",
    description: "Shelf prices as infrastructure. API, CLI, and MCP for AI agents.",
    url: "https://cli-market.dev/impact",
  },
};

export default function ImpactLayout({ children }: { children: React.ReactNode }) {
  return children;
}
