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
    label: "CLI Market API",
    hint_es: "Developers · API · CLI",
    hint_en: "Developers · API · CLI",
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
    intro_es: "Para restaurantes, hoteles y equipos de compras. Misma data que CLI Market API, con aprobaciones, checkout y trazabilidad. Compare $29/mes · Ops $79/mes · Scale $149/mes.",
    intro_en: "For restaurants, hotels, and procurement teams. Same data as CLI Market API, with approvals, checkout, and audit trail. Compare $29/mo · Ops $79/mo · Scale $149/mo.",
    hash: "#procure",
  },
];

export function isLegacyListedPricingHash(hash: string): boolean {
  const h = hash.replace("#", "");
  return h === "listed" || h === "retailers";
}

export function resolvePricingAudience(): PricingAudience {
  if (typeof window === "undefined") return "procure";
  const hash = window.location.hash.replace("#", "");
  const param = new URLSearchParams(window.location.search).get("audience");
  if (hash === "build" || param === "build") return "build";
  return "procure";
}

export function hashForAudience(audience: PricingAudience): string {
  return PRICING_TABS.find((t) => t.id === audience)?.hash ?? "#pricing";
}
