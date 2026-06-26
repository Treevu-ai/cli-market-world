import { redirect } from "next/navigation";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

// Procure Copilot is a separate product with its own site. cli-market.dev keeps
// a single bridge: /procure forwards purchasing/ops visitors to that site so the
// developer landing stays focused on the API/MCP audience.
export default function ProcurePage() {
  redirect(`${PROCURE_SITE_URL}/procure`);
}
