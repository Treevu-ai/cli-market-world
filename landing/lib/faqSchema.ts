import { MARKET_STATS } from "@/lib/marketStats";

export const FAQ_SCHEMA_ES = [
  {
    q: "¿Qué es CLI Market?",
    a: `CLI Market es una API y CLI que permite a agentes de IA buscar, comparar y comprar productos en ${MARKET_STATS.retailersPhraseEs}. Precios de góndola normalizados por unidad. Una sola API. Cero scraping.`,
  },
  {
    q: "¿Con qué retailers funciona?",
    a: `${MARKET_STATS.retailersDefined} retailers en catálogo, ${MARKET_STATS.retailersVerified} verificados activos. ${MARKET_STATS.platformsPhraseEs}.`,
  },
  {
    q: "¿Cómo funciona el pago?",
    a: `Aceptamos ${MARKET_STATS.paymentsLabel}. El checkout genera un QR que escaneas desde tu app de pagos.`,
  },
  {
    q: "¿Los precios son reales?",
    a: `Sí. El collector corre cada ${MARKET_STATS.pricesRefreshHours} horas contra ${MARKET_STATS.retailersVerified} retailers verificados. ${MARKET_STATS.pricesVerifiedLabel} precios normalizados por kg/L.`,
  },
  {
    q: "¿Cuánto cuesta?",
    a: "La CLI es open source (MIT). Free: 1,000 consultas/día. Starter: USD 29/mes (5,000/día, CSV). Pro: USD 79/mes con checkout y export.",
  },
];

export const FAQ_SCHEMA_EN = [
  {
    q: "What is CLI Market?",
    a: `CLI Market is an API and CLI that lets AI agents search, compare, and buy products across ${MARKET_STATS.retailersPhraseEn}. Unit-normalized shelf prices. One API. Zero scraping.`,
  },
  {
    q: "Which retailers do you support?",
    a: `${MARKET_STATS.retailersDefined} retailers in catalog, ${MARKET_STATS.retailersVerified} verified active. ${MARKET_STATS.platformsPhraseEn}.`,
  },
  {
    q: "How does payment work?",
    a: `${MARKET_STATS.paymentsLabel}. Checkout generates a QR code you scan from your payment app.`,
  },
  {
    q: "Are the prices real?",
    a: `Yes. The collector runs every ${MARKET_STATS.pricesRefreshHours} hours against ${MARKET_STATS.retailersVerified} verified retailers. ${MARKET_STATS.pricesVerifiedLabel} prices normalized per kg/L.`,
  },
  {
    q: "How much does it cost?",
    a: "The CLI is open source (MIT). Free: 1,000 requests/day. Starter: USD 29/mo (5,000/day, CSV). Pro: USD 79/mo with checkout and export.",
  },
];

export function buildFaqJsonLd(lang: "es" | "en" = "es") {
  const items = lang === "es" ? FAQ_SCHEMA_ES : FAQ_SCHEMA_EN;
  return {
    "@type": "FAQPage",
    mainEntity: items.map(({ q, a }) => ({
      "@type": "Question",
      name: q,
      acceptedAnswer: { "@type": "Answer", text: a },
    })),
  };
}
