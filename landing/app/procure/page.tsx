import { redirect } from "next/navigation";

// Procure Copilot is a separate product with its own site. cli-market.dev keeps
// a single bridge: /procure forwards purchasing/ops visitors to that site so the
// developer landing stays focused on the API/MCP audience.
// Phase 2 swaps this for the canonical procurecopilot.com domain.
export default function ProcurePage() {
  redirect("https://procure-copilot.contacto-8e4.workers.dev/procure");
}
