import type { Metadata } from "next";
import HouseholdDashboard from "./HouseholdDashboard";

export const metadata: Metadata = {
  title: "Mi hogar — CLI Market",
  description: "Configura tu perfil de hogar: tamaño, presupuesto, restricciones y retailers preferidos.",
  alternates: { canonical: "/dashboard/household" },
};

export default function HouseholdPage() {
  return <HouseholdDashboard />;
}
