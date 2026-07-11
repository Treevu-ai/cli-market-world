import type { Metadata } from "next";
import ExplorerDashboard from "./ExplorerDashboard";

export const metadata: Metadata = {
  title: "Explorer — CLI Market Console",
  description: "Buscá productos, compará precios entre retailers y armá tu canasta óptima en LATAM.",
  alternates: { canonical: "/dashboard/explorer" },
};

export default function ExplorerPage() {
  return <ExplorerDashboard />;
}
