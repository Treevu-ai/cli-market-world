export type PricingAudience = "build" | "procure";

export type PricingTab = {
  id: PricingAudience;
  /** Product-line name on the toggle (chic, short). */
  label: string;
  hint_es: string;
  hint_en: string;
  title_es: string;
  title_en: string;
  intro_es: string;
  intro_en: string;
  hash: string;
};

export const PRICING_TABS: PricingTab[] = [
  {
    id: "build",
    label: "Build",
    hint_es: "API · MCP · agentes",
    hint_en: "API · MCP · agents",
    title_es: "Construido para escalar.",
    title_en: "Built to scale.",
    intro_es: "Para developers y agentes: API REST, CLI y MCP. Free · Starter $24/mes · Pro Founding $29/mes (100 plazas) · Pro $39/mes · Enterprise a medida.",
    intro_en: "For developers and agents: REST API, CLI, and MCP. Free · Starter $24/mo · Pro Founding $29/mo (100 seats) · Pro $39/mo · Enterprise custom.",
    hash: "#pricing",
  },
  {
    id: "procure",
    label: "Procure",
    hint_es: "Compras · aprobaciones",
    hint_en: "Buying · approvals",
    title_es: "Compras de empresa. Sin programar.",
    title_en: "Enterprise buying. No code.",
    intro_es: "Para restaurantes, hoteles y equipos de compras. Misma data que Build, con gobernanza y trazabilidad.",
    intro_en: "For restaurants, hotels, and procurement teams. Same data as Build, with governance and audit trail.",
    hash: "#procure",
  },
];

/** Legacy hashes from when Listed lived under #pricing — retailer signup is on /retailers. */
export function isLegacyListedPricingHash(hash: string): boolean {
  const h = hash.replace("#", "");
  return h === "listed" || h === "retailers";
}

export function resolvePricingAudience(): PricingAudience {
  if (typeof window === "undefined") return "build";
  const hash = window.location.hash.replace("#", "");
  const param = new URLSearchParams(window.location.search).get("audience");
  if (hash === "procure" || param === "procure") return "procure";
  return "build";
}

export function hashForAudience(audience: PricingAudience): string {
  return PRICING_TABS.find((t) => t.id === audience)?.hash ?? "#pricing";
}
