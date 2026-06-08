/** Procure Copilot — pricing on cli-market.dev/#procure (single commercial surface). */

export const PROCURE_APP_URL =
  process.env.NEXT_PUBLIC_PROCURE_APP_URL ||
  "https://procure-copilot.contacto-8e4.workers.dev/dashboard";

export const PROCURE_PLANS = [
  {
    slug: "starter" as const,
    name: "Starter",
    price: 29,
    description_es: "Comparar precios y calcular ahorro — sin checkout.",
    description_en: "Compare prices and savings — no checkout.",
    features_es: [
      "20 procurement/mes",
      "3 retailers por consulta",
      "Infra CLI Market incluida",
      "Sin checkout (upgrade a Pro)",
    ],
    features_en: [
      "20 procurements/mo",
      "3 retailers per query",
      "CLI Market infra included",
      "No checkout (upgrade to Pro)",
    ],
    highlighted: false,
  },
  {
    slug: "pro" as const,
    name: "Pro",
    price: 79,
    description_es: "Aprobaciones, stock, delivery y pago integrado.",
    description_en: "Approvals, stock, delivery, and integrated checkout.",
    features_es: [
      "200 procurement/mes",
      "Flujo run → approve → checkout",
      "PayPal · Mercado Pago · Yape/Plin",
      "Sin suscripción API aparte",
    ],
    features_en: [
      "200 procurements/mo",
      "run → approve → checkout flow",
      "PayPal · Mercado Pago · Yape/Plin",
      "No separate API subscription",
    ],
    highlighted: true,
  },
  {
    slug: "builder" as const,
    name: "Builder",
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