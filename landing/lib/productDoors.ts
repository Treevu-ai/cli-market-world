import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export type ProductDoorId = "build" | "procure" | "advisor";

export type ProductDoor = {
  id: ProductDoorId;
  eyebrow_es: string;
  eyebrow_en: string;
  title_es: string;
  title_en: string;
  pain_es: string;
  pain_en: string;
  outcome_es: string;
  outcome_en: string;
  price_es: string;
  price_en: string;
  cta_es: string;
  cta_en: string;
  href: string;
  external?: boolean;
};

export const PRODUCT_DOORS: ProductDoor[] = [
  {
    id: "build",
    eyebrow_es: "CLI Build",
    eyebrow_en: "CLI Build",
    title_es: "Integra en tu agente",
    title_en: "Integrate into your agent",
    pain_es: "Scraping frágil y precios que alucinan.",
    pain_en: "Fragile scraping and hallucinated prices.",
    outcome_es: "API, MCP y SDK sobre precios normalizados por kg/L.",
    outcome_en: "API, MCP, and SDK on kg/L-normalized prices.",
    price_es: "Starter $9 · Pro $39/mes",
    price_en: "Starter $9 · Pro $39/mo",
    cta_es: "Obtener API Key →",
    cta_en: "Get API Key →",
    href: "/build#pricing",
  },
  {
    id: "procure",
    eyebrow_es: "Procure Copilot",
    eyebrow_en: "Procure Copilot",
    title_es: "Compra sin programar",
    title_en: "Buy without code",
    pain_es: "WhatsApp, Excel y aprobaciones dispersas.",
    pain_en: "WhatsApp, spreadsheets, and scattered approvals.",
    outcome_es: "Comparar, aprobar y pagar en un solo flujo.",
    outcome_en: "Compare, approve, and pay in one flow.",
    price_es: "Desde $29/mes · API incluida",
    price_en: "From $29/mo · API included",
    cta_es: "Ver Procure →",
    cta_en: "See Procure →",
    href: `${PROCURE_SITE_URL}/procure`,
    external: true,
  },
  {
    id: "advisor",
    eyebrow_es: "Asesores",
    eyebrow_en: "Advisors",
    title_es: "Señales antes del IPC",
    title_en: "Signals before CPI",
    pain_es: "Paneles caros y datos oficiales con semanas de retraso.",
    pain_en: "Expensive panels and official data weeks behind.",
    outcome_es: "Inflación, spreads y canasta desde góndola real.",
    outcome_en: "Inflation, spreads, and basket from real shelf data.",
    price_es: "Piloto desde $300/mes",
    price_en: "Pilot from $300/mo",
    cta_es: "Solicitar piloto →",
    cta_en: "Request pilot →",
    href: "/advisor",
  },
];
