import type { Metadata } from "next";
import ProcureCopilotPage from "@/components/ProcureCopilotPage";

export const metadata: Metadata = {
  title: "Procure Copilot",
  description: "Enterprise procurement for LATAM. Request → Compare → Approve → Checkout → Savings. Compare $29 · Ops $79/mo.",
  alternates: { canonical: "/procure" },
  openGraph: {
    title: "Procure Copilot — CLI Market",
    description: "Buy better. Faster. With less waste. Procurement workflows with real shelf prices across 41 verified LATAM retailers.",
  },
};

export default function ProcurePage() {
  return <ProcureCopilotPage />;
}
