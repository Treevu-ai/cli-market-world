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
    label: "Build",
    hint_es: "API · CLI · datos",
    hint_en: "API · CLI · data",
    title_es: "Inteligencia de retail programable.",
    title_en: "Programmable retail intelligence.",
    intro_es: "Sandbox free · Starter $9/mes (14d trial) · Pro $49/mes · Enterprise custom. API, CLI, datos normalizados, basket optimization.",
    intro_en: "Sandbox free · Starter $9/mo (14d trial) · Pro $49/mo · Enterprise custom. API, CLI, normalized data, basket optimization.",
    hash: "#pricing",
  },
  {
    id: "procure",
    label: "Procure",
    hint_es: "Compras · aprobaciones",
    hint_en: "Buying · approvals",
    title_es: "Compras de empresa. Sin programar.",
    title_en: "Enterprise buying. No code.",
    intro_es: "Para restaurantes, hoteles y equipos de compras. Misma data que Build, con gobernanza y trazabilidad. Add-on desde +$79/mes.",
    intro_en: "For restaurants, hotels, and procurement teams. Same data as Build, with governance and audit trail. Add-on from +$79/mo.",
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
