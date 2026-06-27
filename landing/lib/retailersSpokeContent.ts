import { MARKET_STATS } from "@/lib/marketStats";

export type SpokeStepContent = {
  n: string;
  title_es: string;
  title_en: string;
  body_es: string;
  body_en: string;
};

export type SpokeBenefitContent = {
  title_es: string;
  title_en: string;
  body_es: string;
  body_en: string;
};

export const RETAILERS_STEPS_SECTION = {
  id: "how-it-works",
  eyebrow_es: "PROCESO",
  eyebrow_en: "HOW IT WORKS",
  title_es: "Cómo aparecer",
  title_en: "How to get listed",
  intro_es: "Tres pasos — sin integración técnica de tu parte.",
  intro_en: "Three steps — no technical integration on your side.",
  steps: [
    {
      n: "1",
      title_es: "Completa el formulario",
      title_en: "Fill out the form",
      body_es:
        "Nombre de tu tienda, URL, categoría de productos y país. Menos de 2 minutos. Sin datos sensibles.",
      body_en:
        "Store name, URL, product category, and country. Less than 2 minutes. No sensitive data.",
    },
    {
      n: "2",
      title_es: "Nuestro equipo verifica tu catálogo",
      title_en: "Our team verifies your catalog",
      body_es:
        "Indexamos tus productos con precios normalizados por unidad (kg, L, unidad). Te confirmamos en 24–48 horas.",
      body_en:
        "We index your products with unit-normalized prices (kg, L, unit). We confirm within 24–48 hours.",
    },
    {
      n: "3",
      title_es: "Tus productos aparecen en búsquedas",
      title_en: "Your products appear in searches",
      body_es:
        "Compradores empresariales, agentes de IA y herramientas de procurement encuentran tus productos y los comparan contra tu competencia.",
      body_en:
        "Business buyers, AI agents, and procurement tools find your products and compare them against your competition.",
    },
  ] satisfies SpokeStepContent[],
};

export const RETAILERS_BENEFITS_SECTION = {
  eyebrow_es: "POR QUÉ APARECER",
  eyebrow_en: "WHY GET LISTED",
  title_es: "Lo que obtienes",
  title_en: "What you get",
  benefits: [
    {
      title_es: "Visibilidad en canales de IA",
      title_en: "Visibility in AI channels",
      body_es:
        "Los agentes de IA comparan productos automáticamente para compradores empresariales. Tus productos aparecen en sus resultados — como el SEO de la era de agentes. Cada día que no estás, tu competidor sí.",
      body_en:
        "AI agents automatically compare products for business buyers. Your products appear in their results — like SEO for the agent era. Every day you're not here, your competitor is.",
    },
    {
      title_es: "Inteligencia competitiva en tiempo real",
      title_en: "Real-time competitive intelligence",
      body_es: `Ve cómo tus precios se posicionan frente a ${MARKET_STATS.retailersVerified} retailers verificados. Detecta spread de precios, identifica oportunidades y ajusta antes de perder ventas frente a un rival que ya sí está indexado.`,
      body_en: `See how your prices position against ${MARKET_STATS.retailersVerified} verified retailers. Detect price spreads, spot opportunities, and adjust before losing sales to an already-indexed competitor.`,
    },
    {
      title_es: "Sin integración técnica requerida",
      title_en: "No technical integration required",
      body_es:
        "Completa un formulario. Nuestro equipo indexa tu catálogo sin que muevas un dedo. Sin SDK, sin APIs, sin desarrolladores. Gratis para siempre.",
      body_en:
        "Fill out a form. Our team indexes your catalog without you lifting a finger. No SDK, no APIs, no developers. Free forever.",
    },
  ] satisfies SpokeBenefitContent[],
};

export const RETAILERS_STATS = (isES: boolean) => [
  { n: String(MARKET_STATS.retailersVerified), l: isES ? "Retailers activos" : "Retailers live" },
  { n: MARKET_STATS.pricesVerifiedLabel, l: isES ? "Precios indexados" : "Prices indexed" },
  { n: String(MARKET_STATS.countries), l: isES ? "Países" : "Countries" },
  { n: `${MARKET_STATS.pricesRefreshHours}h`, l: isES ? "Actualización de precios" : "Price refresh" },
];
