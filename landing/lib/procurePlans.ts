/** Procure Copilot — pricing tab at cli-market.dev/#procure (inside #pricing). */

export const PROCURE_APP_URL =
  process.env.NEXT_PUBLIC_PROCURE_APP_URL ||
  "https://procure-copilot.contacto-8e4.workers.dev/dashboard";

/** Display names avoid collision with Build tiers (Starter / Pro). Slugs unchanged for API. */
export const PROCURE_PLANS = [
  {
    slug: "starter" as const,
    name: "Compare",
    price: 29,
    description_es: "Comparar precios y calcular ahorro — sin checkout.",
    description_en: "Compare prices and savings — no checkout.",
    features_es: [
      "20 procurement/mes",
      "3 retailers por consulta",
      "Infra CLI Market incluida",
      "Sin checkout (upgrade a Ops)",
    ],
    features_en: [
      "20 procurements/mo",
      "3 retailers per query",
      "CLI Market infra included",
      "No checkout (upgrade to Ops)",
    ],
    highlighted: false,
  },
  {
    slug: "pro" as const,
    name: "Ops",
    price: 79,
    description_es: "Aprobaciones, stock, delivery y pago integrado.",
    description_en: "Approvals, stock, delivery, and integrated checkout.",
    features_es: [
      "200 procurement/mes",
      "Flujo run → approve → checkout",
      "PayPal (USD) · Mercado Pago (soles)",
      "Sin suscripción Build aparte",
    ],
    features_en: [
      "200 procurements/mo",
      "run → approve → checkout flow",
      "PayPal (USD) · Mercado Pago (soles)",
      "No separate Build subscription",
    ],
    highlighted: true,
  },
  {
    slug: "builder" as const,
    name: "Scale",
    price: 149,
    description_es: "Multi-país y alto volumen.",
    description_en: "Multi-country and high volume.",
    features_es: [
      "1,000 procurement/mes",
      "Integraciones",
      "SLA 99.5%",
    ],
    features_en: [
      "1,000 procurements/mo",
      "Integrations",
      "99.5% SLA",
    ],
    highlighted: false,
  },
] as const;

export type ProcurePlanSlug = (typeof PROCURE_PLANS)[number]["slug"];
