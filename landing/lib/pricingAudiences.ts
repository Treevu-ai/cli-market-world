export type PricingAudience = "build" | "procure" | "listed";

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
    intro_es: "Integra precios de góndola en tu agente o producto. Free para empezar, Pro cuando necesites checkout.",
    intro_en: "Plug shelf prices into your agent or product. Free to start, Pro when you need checkout.",
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
  {
    id: "listed",
    label: "Listed",
    hint_es: "Góndola visible · $0",
    hint_en: "Shelf visible · $0",
    title_es: "Tu góndola, en el radar de los agentes.",
    title_en: "Your shelf, on every agent's radar.",
    intro_es: "VTEX, Shopify, Magento o WooCommerce — 30 segundos, sin código, gratis para siempre.",
    intro_en: "VTEX, Shopify, Magento, or WooCommerce — 30 seconds, no code, free forever.",
    hash: "#listed",
  },
];

export function resolvePricingAudience(): PricingAudience {
  if (typeof window === "undefined") return "build";
  const hash = window.location.hash.replace("#", "");
  const param = new URLSearchParams(window.location.search).get("audience");
  if (hash === "procure" || param === "procure") return "procure";
  if (hash === "listed" || hash === "retailers" || param === "listed" || param === "retailers") {
    return "listed";
  }
  return "build";
}

export function hashForAudience(audience: PricingAudience): string {
  return PRICING_TABS.find((t) => t.id === audience)?.hash ?? "#pricing";
}