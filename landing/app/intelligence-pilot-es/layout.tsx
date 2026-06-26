import type { Metadata } from "next";
import { MARKET_STATS } from "@/lib/marketStats";

export const metadata: Metadata = {
  title: "Intelligence Pilot — CLI Market",
  description: `Piloto Intelligence desde USD 300/mes. Spreads, inflación y canasta desde góndola LATAM. ${MARKET_STATS.pricesVerifiedLabel} precios · ${MARKET_STATS.retailersVerified} retailers verificados.`,
  alternates: {
    canonical: "https://cli-market.dev/intelligence-pilot-es",
  },
  openGraph: {
    title: "CLI Market Intelligence — Piloto",
    description: "One-pager del piloto Intelligence para pricing, fintech y consultoras.",
    url: "https://cli-market.dev/intelligence-pilot-es",
  },
};

export default function IntelligencePilotLayout({ children }: { children: React.ReactNode }) {
  return children;
}
