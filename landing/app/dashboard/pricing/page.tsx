import type { Metadata } from "next";
import PricingDashboard from "./PricingDashboard";

export const metadata: Metadata = {
  title: "Pricing & Brand Intelligence — CLI Market",
  description: "Compará marcas y tiendas, seguí tendencias de precio y ajustá las palancas de tu estrategia de pricing en LATAM.",
  alternates: { canonical: "/dashboard/pricing" },
};

export default function PricingPage() {
  return <PricingDashboard />;
}
