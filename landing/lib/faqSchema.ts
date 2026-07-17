import { paymentsChannelsShort, sinapsisBillingPolicy } from "@/lib/billingCopy";

const billingEs = `${sinapsisBillingPolicy(true)} Canales: ${paymentsChannelsShort(true)}.`;
const billingEn = `${sinapsisBillingPolicy(false)} Channels: ${paymentsChannelsShort(false)}.`;

export const FAQ_SCHEMA_ES = [
  {
    q: "¿Qué es CLI Market?",
    a: "Infraestructura de precios retail: CLI Build (MCP y API), Procure Copilot (compras) y Advisors (datos y reportes).",
  },
  {
    q: "¿Cómo empiezo?",
    a: "pip install cli-market-world, API key en el dashboard y MCP en tu IDE. Sin contrato ni demo obligatoria.",
  },
  {
    q: "¿Cómo funciona el pago y la facturación?",
    a: billingEs,
  },
  {
    q: "¿Cuánto cuesta?",
    a: "CLI Build desde $9/mes. Procure Copilot desde $29/mes. Advisors desde $300/mes. Cancela cuando quieras.",
  },
];

export const FAQ_SCHEMA_EN = [
  {
    q: "What is CLI Market?",
    a: "Retail price infrastructure: CLI Build (MCP and API), Procure Copilot (procurement), and Advisors (data and reports).",
  },
  {
    q: "How do I get started?",
    a: "pip install cli-market-world, API key in the dashboard, and MCP in your IDE. No contract or mandatory demo.",
  },
  {
    q: "How do payments and billing work?",
    a: billingEn,
  },
  {
    q: "How much does it cost?",
    a: "CLI Build from $9/mo. Procure Copilot from $29/mo. Advisors from $300/mo. Cancel anytime.",
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