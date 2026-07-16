/**
 * Retailer pricing tiers. Free stays free forever (existing listing flow,
 * unchanged). Growth has a real Mercado Pago checkout (see
 * components/retailers/RetailersPricingSection.tsx + POST
 * /billing/retailer-growth-checkout) — activation is manual on our side
 * (team flips the listing to Growth on payment confirmation), since
 * retailers have no CLI account/plan concept today. Custom routes to a
 * dedicated contact-form topic instead of a checkout.
 */

export type RetailerTierId = "free" | "growth" | "custom";

export type RetailerTierSpec = {
  id: RetailerTierId;
  name: string;
  priceUsd: number | null;
  period_es?: string;
  period_en?: string;
  features_es: string[];
  features_en: string[];
  featured?: boolean;
  cta_es: string;
  cta_en: string;
};

export const RETAILER_TIER_FREE: RetailerTierSpec = {
  id: "free",
  name: "Free",
  priceUsd: 0,
  period_es: "gratis para siempre",
  period_en: "free forever",
  features_es: [
    "Listado básico en CLI Market",
    "Precios normalizados por unidad (kg, L)",
    "Refresh cada 4h",
    "Visible para agentes de IA y compradores",
  ],
  features_en: [
    "Basic listing on CLI Market",
    "Unit-normalized prices (kg, L)",
    "4h refresh",
    "Visible to AI agents and buyers",
  ],
  cta_es: "Listar mi tienda — gratis",
  cta_en: "List my store — free",
};

export const RETAILER_TIER_GROWTH: RetailerTierSpec = {
  id: "growth",
  name: "Growth",
  priceUsd: 9,
  period_es: "/ mes",
  period_en: "/ mo",
  features_es: [
    "Todo lo de Free",
    "Prioridad de indexación en resultados",
    "Dashboard de tus precios vs. la competencia",
    "Refresh más frecuente",
    "Badge de retailer verificado",
  ],
  features_en: [
    "Everything in Free",
    "Priority indexing in results",
    "Your prices vs. competitors dashboard",
    "More frequent refresh",
    "Verified retailer badge",
  ],
  featured: true,
  cta_es: "Elegir Growth — pagar",
  cta_en: "Choose Growth — pay",
};

export const RETAILER_TIER_CUSTOM: RetailerTierSpec = {
  id: "custom",
  name: "Custom",
  priceUsd: null,
  period_es: "",
  period_en: "",
  features_es: [
    "Múltiples tiendas o marcas",
    "Catálogo vía API / carga masiva",
    "SLA y soporte dedicado",
    "Cuenta administrada por el equipo",
  ],
  features_en: [
    "Multiple stores or brands",
    "Catalog via API / bulk upload",
    "Dedicated SLA and support",
    "Account managed by our team",
  ],
  cta_es: "Contactar ventas",
  cta_en: "Contact sales",
};

export const RETAILER_TIERS: RetailerTierSpec[] = [
  RETAILER_TIER_FREE,
  RETAILER_TIER_GROWTH,
  RETAILER_TIER_CUSTOM,
];
