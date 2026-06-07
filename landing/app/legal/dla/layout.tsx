import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Acuerdo de Licencia de Datos / Data License Agreement — CLI Market",
  description:
    "CLI Market Data License Agreement (DLA). Governs use of pricing data, SKU mappings, and historical snapshots.",
  alternates: { canonical: "/legal/dla" },
};

export default function DlaLayout({ children }: { children: React.ReactNode }) {
  return children;
}