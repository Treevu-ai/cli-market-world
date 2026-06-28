export type PricingAudience = "build" | "procure";

export type PricingTab = {
  id: PricingAudience;
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
    label: "CLI Build",
    hint_es: "Build · API · CLI",
    hint_en: "Build · API · CLI",
    title_es: "Inteligencia de retail programable.",
    title_en: "Programmable retail intelligence.",
    intro_es: "Para developers. Free 1.000 req/día · Starter $9/mes (5k/día, 14d trial) · Pro $49/mes · Enterprise custom. API, CLI, datos normalizados por kg/L.",
    intro_en: "For developers. Free 1,000 req/day · Starter $9/mo (5k/day, 14d trial) · Pro $49/mo · Enterprise custom. API, CLI, normalized per kg/L data.",
    hash: "#pricing",
  },
  {
    id: "procure",
    label: "Procure Copilot",
    hint_es: "Equipos de compras",
    hint_en: "Procurement teams",
    title_es: "Compras de empresa. Sin programar.",
    title_en: "Enterprise buying. No code.",
    intro_es: "Misma data que CLI Build, interfaz para compras. Compare $29/mes · Ops $79/mes · Scale $149/mes.",
    intro_en: "Same data as CLI Build, interface for procurement. Compare $29/mo · Ops $79/mo · Scale $149/mo.",
    hash: "#pricing",
  },
];

export function isLegacyListedPricingHash(hash: string): boolean {
  const h = hash.replace("#", "");
  return h === "listed" || h === "retailers";
}

export function resolvePricingAudience(): PricingAudience {
  // Procure checkout lives on procurecopilot.com/subscribe (Phase 2). Legacy
  // ?audience=procure on /build redirects to the sister site.
  if (typeof window === "undefined") return "build";
  const param = new URLSearchParams(window.location.search).get("audience");
  return param === "procure" ? "procure" : "build";
}

export function hashForAudience(audience: PricingAudience): string {
  return PRICING_TABS.find((t) => t.id === audience)?.hash ?? "#pricing";
}
