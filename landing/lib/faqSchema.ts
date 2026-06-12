import { MARKET_STATS } from "@/lib/marketStats";
import { paymentsChannelsShort, sinapsisBillingPolicy } from "@/lib/billingCopy";

const billingEs = `${sinapsisBillingPolicy(true)} Canales: ${paymentsChannelsShort(true)}.`;
const billingEn = `${sinapsisBillingPolicy(false)} Channels: ${paymentsChannelsShort(false)}.`;

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
    q: "¿Cómo funciona el pago y la facturación?",
    a: billingEs,
  },
  {
    q: "¿Los precios son reales?",
    a: `Sí. El collector corre cada ${MARKET_STATS.pricesRefreshHours} horas contra ${MARKET_STATS.retailersVerified} retailers verificados. ${MARKET_STATS.pricesVerifiedLabel} precios normalizados por kg/L.`,
  },
  {
    q: "¿Cuánto cuesta?",
    a: "La CLI es open source (MIT). Free: 1.000 consultas/día. Starter: USD 24/mes. Pro: USD 39/mes o USD 390/año. Pro Founding: USD 29/mes (100 plazas). Enterprise a medida.",
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
    q: "How do payments and billing work?",
    a: billingEn,
  },
  {
    q: "Are the prices real?",
    a: `Yes. The collector runs every ${MARKET_STATS.pricesRefreshHours} hours against ${MARKET_STATS.retailersVerified} verified retailers. ${MARKET_STATS.pricesVerifiedLabel} prices normalized per kg/L.`,
  },
  {
    q: "How much does it cost?",
    a: "The CLI is open source (MIT). Free: 1,000 requests/day. Starter: USD 24/mo. Pro: USD 39/mo or USD 390/yr. Pro Founding: USD 29/mo (100 seats). Enterprise custom.",
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
