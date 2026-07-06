import type { Metadata } from "next";
import BrandMonitorDashboard from "@/components/brand/BrandMonitorDashboard";

export const metadata: Metadata = {
  title: "Brand Monitor — CLI Market",
  description:
    "Monitor de precios de marca en góndola digital. Tus SKUs vs competidores, cada 8 horas.",
  robots: { index: false, follow: false },
};

// Static export: generateStaticParams is required when using [slug] with output: "export".
// We export a sentinel page; the actual slug is read client-side from the URL.
export function generateStaticParams() {
  return [{ slug: "demo" }];
}

export default function BrandMonitorPage() {
  return <BrandMonitorDashboard />;
}
