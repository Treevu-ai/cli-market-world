import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export type CaseStudyProduct = "build" | "procure" | "intelligence" | "retailers";

export type CaseStudyMetric = {
  value: string;
  label_es: string;
  label_en: string;
};

export type CaseStudy = {
  id: string;
  product: CaseStudyProduct;
  icon: string;
  client_es: string;
  client_en: string;
  problem_es: string;
  problem_en: string;
  solution_es: string;
  solution_en: string;
  metrics: CaseStudyMetric[];
};

const { retailersVerified, countries, pricesVerifiedLabel, pricesRefreshHours, mcpTools } = MARKET_STATS;

export const CASE_STUDY_PRODUCT_LABELS: Record<
  CaseStudyProduct,
  { es: string; en: string; className: string }
> = {
  build: { es: "Build", en: "Build", className: "text-[var(--cm-mint)] border-[var(--cm-mint)]/30 bg-[var(--cm-mint)]/10" },
  procure: { es: "Procure", en: "Procure", className: "text-[var(--cm-brand-accent)] border-[var(--cm-brand-accent)]/30 bg-[var(--cm-action-soft)]" },
  intelligence: {
    es: "Intelligence",
    en: "Intelligence",
    className: "text-[#38bdf8] border-[#38bdf8]/30 bg-[#38bdf8]/10",
  },
  retailers: {
    es: "Retailers",
    en: "Retailers",
    className: "text-[var(--cm-on-surface-variant)] border-[var(--cm-outline-variant)]/50 bg-[var(--cm-surface-low)]/60",
  },
};

export const CASE_STUDIES: CaseStudy[] = [
  {
    id: "fintech-credit",
    product: "intelligence",
    icon: "📊",
    client_es: "Fintech de credit scoring · Perú",
    client_en: "Credit-scoring fintech · Peru",
    problem_es:
      "Necesitaban canasta básica en tiempo útil para ajustar modelos de riesgo. INEI llega con ~45 días de retraso. Paneles legacy son caros y no cubren ciudades secundarias.",
    problem_en:
      "They needed timely basic-basket data to tune risk models. Official CPI arrives ~45 days late. Legacy panels are expensive and miss secondary cities.",
    solution_es: `Piloto Intelligence: precios históricos de supermercados en Perú y Colombia, refresh cada ${pricesRefreshHours} h. Export JSON/CSV con series de 30–90 días y capa clean / flagged / citable.`,
    solution_en: `Intelligence pilot: supermarket price history in Peru and Colombia, refreshed every ${pricesRefreshHours}h. JSON/CSV export with 30–90 day series and clean / flagged / citable quality layer.`,
    metrics: [
      { value: pricesVerifiedLabel, label_es: "precios indexados", label_en: "prices indexed" },
      { value: "1 día", label_es: "time-to-data vs 45 d INEI", label_en: "time-to-data vs 45 d official CPI" },
      { value: "$300–500", label_es: "piloto/mes vs alternativas anuales", label_en: "pilot/mo vs annual alternatives" },
    ],
  },
  {
    id: "restaurant-procurement",
    product: "procure",
    icon: "🛒",
    client_es: "Automatización de compras · restaurantes",
    client_en: "Purchase automation · restaurants",
    problem_es:
      "Cada local comparaba precios manualmente entre 3–5 proveedores. 4–6 horas/semana en WhatsApp y Excel. Querían un agente que cotice y deje trazabilidad.",
    problem_en:
      "Each location compared prices manually across 3–5 suppliers. 4–6 hours/week on WhatsApp and Excel. They wanted an agent that quotes with audit trail.",
    solution_es: `Procure Starter + API Build: búsqueda en ${retailersVerified} retailers verificados, ${countries} países, alertas >5% y flujo run → approve con data-gate.`,
    solution_en: `Procure Starter + Build API: search across ${retailersVerified} verified retailers, ${countries} countries, >5% alerts, and run → approve flow with data-gate.`,
    metrics: [
      { value: "4–6 h", label_es: "semana recuperadas por local", label_en: "hours/week saved per site" },
      { value: "$29", label_es: "Procure Starter /mes", label_en: "Procure Starter /mo" },
      { value: "3", label_es: "onboarded en mes 1", label_en: "onboarded in month 1" },
    ],
  },
  {
    id: "trade-marketing",
    product: "intelligence",
    icon: "📈",
    client_es: "Trade marketing · consumo masivo",
    client_en: "Trade marketing · FMCG",
    problem_es:
      "Spreads de precio por SKU entre cadenas se medían con scraping ad hoc y hojas compartidas. Sin normalización por kg/L ni reglas de calidad documentadas.",
    problem_en:
      "Price spreads per SKU across chains were tracked with ad hoc scraping and shared sheets. No kg/L normalization or documented quality rules.",
    solution_es:
      "Intelligence Pilot M: spreads min–max por seed comparable, inflación por línea, export semanal + API de lectura. Revisión quincenal de cobertura durante el piloto.",
    solution_en:
      "Intelligence Pilot M: min–max spreads per comparable seed, line inflation, weekly export + read API. Biweekly coverage review during the pilot.",
    metrics: [
      { value: `${countries}`, label_es: "países en alcance piloto", label_en: "countries in pilot scope" },
      { value: "60 d", label_es: "histórico en tier M", label_en: "history on tier M" },
      { value: "48 h", label_es: "onboarding acordado", label_en: "agreed onboarding" },
    ],
  },
  {
    id: "ai-agent-builder",
    product: "build",
    icon: "🤖",
    client_es: "Startup de agentes de compra · LATAM",
    client_en: "Shopping-agent startup · LATAM",
    problem_es:
      "Mantener parsers por retailer consumía el roadmap. Cada cambio de theme VTEX o Shopify rompía flujos de búsqueda y compare.",
    problem_en:
      "Maintaining per-retailer parsers consumed the roadmap. Every VTEX or Shopify theme change broke search and compare flows.",
    solution_es: `API keys + ${mcpTools} API tools (Shop / Intel / Account). El agente usa market_search, market_basket y market_intel_brief sin scraping propio.`,
    solution_en: `API keys + ${mcpTools} API tools (Shop / Intel / Account). The agent uses market_search, market_basket, and market_intel_brief with zero custom scraping.`,
    metrics: [
      { value: String(mcpTools), label_es: "API tools MCP", label_en: "MCP API tools" },
      { value: `${pricesRefreshHours}h`, label_es: "refresh del moat", label_en: "moat refresh" },
      { value: "$49", label_es: "Build Pro /mes", label_en: "Build Pro /mo" },
    ],
  },
  {
    id: "hotel-procurement",
    product: "procure",
    icon: "🏨",
    client_es: "Hotel · compras multi-sede",
    client_en: "Hotel · multi-site procurement",
    problem_es:
      "Gerencia necesitaba aprobar compras >S/ 2,000 con evidencia de precio y stock. El equipo operaba con cotizaciones por chat sin auditoría central.",
    problem_en:
      "Management needed to approve purchases above S/ 2,000 with price and stock evidence. Ops ran on chat quotes with no central audit trail.",
    solution_es: `Procure Pro ($79/mes): flujo run → pending_approval → checkout, verificación de stock y delivery, infra Build Pro incluida.`,
    solution_en: `Procure Pro ($79/mo): run → pending_approval → checkout flow, stock and delivery checks, Build Pro infra included.`,
    metrics: [
      { value: "run → approve", label_es: "trazabilidad por compra", label_en: "traceability per purchase" },
      { value: "$79", label_es: "Procure Pro /mes", label_en: "Procure Pro /mo" },
      { value: "3", label_es: "países en plan Procure Pro", label_en: "countries on Procure Pro plan" },
    ],
  },
  {
    id: "retailer-listing",
    product: "retailers",
    icon: "🏪",
    client_es: "E-commerce VTEX · Perú",
    client_en: "VTEX e-commerce · Peru",
    problem_es:
      "Invisible para agentes de IA y herramientas de procurement que comparan góndola. Competidores ya aparecían en búsquedas automatizadas.",
    problem_en:
      "Invisible to AI agents and procurement tools comparing shelf prices. Competitors already showed up in automated searches.",
    solution_es: `Listado gratuito en CLI Market: catálogo indexado con precios normalizados, sin SDK. Aparece en búsquedas de ${retailersVerified} retailers del ecosistema.`,
    solution_en: `Free CLI Market listing: catalog indexed with normalized prices, no SDK. Surfaces in searches across the ${retailersVerified}-retailer ecosystem.`,
    metrics: [
      { value: "24–48 h", label_es: "verificación de catálogo", label_en: "catalog verification" },
      { value: "$0", label_es: "listado retailer", label_en: "retailer listing" },
      { value: "VTEX", label_es: "plataforma soportada", label_en: "supported platform" },
    ],
  },
];

export const CASE_STUDIES_CTA = {
  intelligence: {
    href: "/contact?topic=intelligence#contact-intelligence",
    es: "Solicitar piloto Intelligence",
    en: "Request Intelligence pilot",
  },
  procure: {
    href: `${PROCURE_SITE_URL}/procure#pricing`,
    es: "Ver planes Procure",
    en: "See Procure plans",
  },
  build: {
    href: "/build#pricing",
    es: "Ver planes Build",
    en: "See Build plans",
  },
  retailers: {
    href: "/retailers",
    es: "Aplicar como retailer",
    en: "Apply as retailer",
  },
} as const;
