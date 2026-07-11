import type { Metadata } from "next";
import DeveloperDashboard from "./DeveloperDashboard";

export const metadata: Metadata = {
  title: "Developer — CLI Market Console",
  description: "Gestioná tus API keys y generá la configuración MCP para Claude, Cursor u otro cliente.",
  alternates: { canonical: "/dashboard/developer" },
};

export default function DeveloperPage() {
  return <DeveloperDashboard />;
}
